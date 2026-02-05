"""
Base LLM provider abstraction for LinkBrain Core.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

__all__ = ['LLMConfig', 'BaseLLMProvider']


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    model: str
    temperature: float = 0.1
    max_tokens: int = 500
    timeout: float = 30.0
    extra_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers in LinkBrain.
    
    LLM providers translate natural language into structured intent
    that can be validated and executed by the framework.
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize LLM provider.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        logger.info(f"LLM provider initialized: {config.model}")

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt with device context
        
        Returns:
            Generated text response
        
        Raises:
            LLMGenerationError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_structured(
        self, 
        prompt: str, 
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from LLM.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema for validation
        
        Returns:
            Parsed JSON response
        
        Raises:
            LLMParsingError: If generation or parsing fails
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate provider connection and credentials.
        
        Returns:
            True if connection is valid
        """
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(model='{self.config.model}')"