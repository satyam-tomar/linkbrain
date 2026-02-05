"""
Base tool device abstraction for AI layer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

__all__ = ['BaseToolDevice']


class BaseToolDevice(ABC):
    """
    Abstract base class for AI-controllable tool devices.
    
    This wraps a physical device and exposes actions to the AI layer.
    Tools provide a higher-level interface than raw devices.
    """

    def __init__(self, name: str):
        """
        Initialize tool device.
        
        Args:
            name: Human-readable tool name
        """
        self.name = name
        logger.debug(f"Tool '{name}' initialized")

    @abstractmethod
    async def on(self) -> None:
        """Execute 'on' action."""
        pass

    @abstractmethod
    async def off(self) -> None:
        """Execute 'off' action."""
        pass

    @abstractmethod
    async def status(self) -> Dict[str, Any]:
        """Get current status."""
        pass

    @abstractmethod
    def supported_actions(self) -> set[str]:
        """
        Get supported actions.
        
        Returns:
            Set of action names (e.g., {"on", "off", "status"})
        """
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}('{self.name}')"
