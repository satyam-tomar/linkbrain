"""
Google Gemini LLM provider for LinkBrain Core.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "Google Generative AI not installed. "
        "Install with: pip install google-generativeai"
    )

from linkbrain_core.llm.base import BaseLLMProvider, LLMConfig
from linkbrain_core.exceptions import (
    LLMConnectionError,
    LLMGenerationError,
    LLMParsingError
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider for LinkBrain.
    
    Translates natural language into structured device control intent.
    """

    def __init__(
        self,
        api_key: str,
        config: Optional[LLMConfig] = None
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key
            config: LLM configuration (defaults to gemini-pro)
        """
        if config is None:
            config = LLMConfig(model="gemini-2.5-flash")
        
        super().__init__(config)
        self.api_key = api_key
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(config.model)
            logger.info(f"Gemini provider initialized: {config.model}")
        except Exception as e:
            raise LLMConnectionError(f"Failed to initialize Gemini: {e}")

    def validate_connection(self) -> bool:
        """Validate Gemini connection."""
        try:
            # Simple test generation
            response = self.model.generate_content(
                "test",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10
                )
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini validation failed: {e}")
            return False

    async def generate(self, prompt: str) -> str:
        """
        Generate text response from Gemini.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        
        Raises:
            LLMGenerationError: If generation fails
        """
        try:
            logger.debug(f"Gemini prompt length: {len(prompt)}")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens,
                    )
                )
            )
            
            result = response.text.strip()
            logger.debug(f"Gemini response length: {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise LLMGenerationError(f"Generation failed: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Gemini.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema (not enforced by Gemini)
        
        Returns:
            Parsed JSON object
        
        Raises:
            LLMParsingError: If JSON parsing fails
        """
        raw_response = await self.generate(prompt)
        
        try:
            # Clean markdown code blocks if present
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Optional schema validation would go here
            if schema:
                # Could use jsonschema library for validation
                pass
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON: {raw_response}")
            raise LLMParsingError(f"Invalid JSON response: {e}")