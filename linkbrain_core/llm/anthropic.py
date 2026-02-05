"""
Anthropic Claude LLM provider for LinkBrain Core.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional

try:
    import anthropic
except ImportError:
    raise ImportError(
        "Anthropic SDK not installed. "
        "Install with: pip install anthropic"
    )

from linkbrain_core.llm.base import BaseLLMProvider, LLMConfig
from linkbrain_core.exceptions import (
    LLMConnectionError,
    LLMGenerationError,
    LLMParsingError
)

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude LLM provider for LinkBrain.
    """

    def __init__(
        self,
        api_key: str,
        config: Optional[LLMConfig] = None
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            config: LLM configuration (defaults to claude-3-haiku)
        """
        if config is None:
            config = LLMConfig(model="claude-3-haiku-20240307")
        
        super().__init__(config)
        
        try:
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            logger.info(f"Anthropic provider initialized: {config.model}")
        except Exception as e:
            raise LLMConnectionError(f"Failed to initialize Anthropic: {e}")

    def validate_connection(self) -> bool:
        """Validate Anthropic connection."""
        try:
            # Anthropic doesn't have a direct ping, but we can check client
            return self.client is not None
        except Exception as e:
            logger.error(f"Anthropic validation failed: {e}")
            return False

    async def generate(self, prompt: str) -> str:
        """
        Generate text response from Claude.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        
        Raises:
            LLMGenerationError: If generation fails
        """
        try:
            logger.debug(f"Claude prompt length: {len(prompt)}")
            
            message = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = message.content[0].text.strip()
            logger.debug(f"Claude response length: {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise LLMGenerationError(f"Generation failed: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Claude.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema
        
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
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude JSON: {raw_response}")
            raise LLMParsingError(f"Invalid JSON response: {e}")