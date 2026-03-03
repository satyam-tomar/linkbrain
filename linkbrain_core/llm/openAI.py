"""
OpenAI ChatGPT LLM provider for LinkBrain Core.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError(
        "OpenAI SDK not installed. "
        "Install with: pip install openai"
    )

from linkbrain_core.llm.base import BaseLLMProvider, LLMConfig
from linkbrain_core.exceptions import (
    LLMConnectionError,
    LLMGenerationError,
    LLMParsingError
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI ChatGPT provider for LinkBrain.
    
    Translates natural language into structured device control intent.
    """

    def __init__(
        self,
        api_key: str,
        config: Optional[LLMConfig] = None
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            config: LLM configuration (defaults to gpt-4o-mini)
        """
        if config is None:
            config = LLMConfig(model="gpt-4o-mini")

        super().__init__(config)
        self.api_key = api_key

        try:
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info(f"OpenAI provider initialized: {config.model}")
        except Exception as e:
            raise LLMConnectionError(f"Failed to initialize OpenAI: {e}")

    def validate_connection(self) -> bool:
        """Validate OpenAI connection."""
        try:
            # Simple lightweight request
            async def _test():
                resp = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                )
                return bool(resp.choices[0].message.content)

            return asyncio.run(_test())
        except Exception as e:
            logger.error(f"OpenAI validation failed: {e}")
            return False

    async def generate(self, prompt: str) -> str:
        """
        Generate text response from OpenAI.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        
        Raises:
            LLMGenerationError: If generation fails
        """
        try:
            logger.debug(f"OpenAI prompt length: {len(prompt)}")

            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )

            result = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response length: {len(result)}")

            return result

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise LLMGenerationError(f"Generation failed: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from OpenAI.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema (not enforced here)
        
        Returns:
            Parsed JSON object
        
        Raises:
            LLMParsingError: If JSON parsing fails
        """
        raw_response = await self.generate(prompt)

        try:
            cleaned = raw_response.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            if schema:
                # Optional: integrate jsonschema validation here
                pass

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON: {raw_response}")
            raise LLMParsingError(f"Invalid JSON response: {e}")