"""
Google Gemini LLM provider.
"""

import asyncio
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Google Gemini LLM provider for smart home control.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key
            model: Gemini model name (default: gemini-pro)
        """
        self.api_key = api_key
        self.model_name = model
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        
        logger.info(f"Gemini provider initialized with model: {model}")
    
    async def generate(self, prompt: str, temperature: float = 0.1) -> str:
        """
        Generate response from Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Generation temperature (0.0-1.0)
        
        Returns:
            Generated text response
        
        Raises:
            Exception: If generation fails
        """
        try:
            logger.debug(f"Sending prompt to Gemini (length: {len(prompt)})")
            
            # Generate response (sync call in thread pool)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=500,
                    )
                )
            )
            
            result = response.text.strip()
            logger.debug(f"Gemini response (length: {len(result)})")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise