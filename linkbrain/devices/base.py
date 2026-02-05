"""
Base device abstraction for LinkBrain.

All physical device implementations must inherit from BaseDevice.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import DeviceError

logger = logging.getLogger(__name__)

__all__ = ['BaseDevice']


class BaseDevice(ABC):
    """
    Abstract base class for all physical devices.
    
    Devices represent physical hardware (lights, fans, doors, etc.)
    and provide high-level control interfaces.
    """
    
    def __init__(
        self,
        name: str,
        controller: ESP32Controller,
        pin: Optional[int] = None
    ):
        """
        Initialize base device.
        
        Args:
            name: Human-readable device name
            controller: ESP32 controller instance
            pin: GPIO pin number (if applicable)
        """
        self.name = name
        self.controller = controller
        self.pin = pin
        self._state: Dict[str, Any] = {}
        
        logger.info(f"Device '{name}' initialized")
    
    @abstractmethod
    def on(self) -> None:
        """
        Turn device on or activate it.
        
        Raises:
            DeviceError: If operation fails
        """
        pass
    
    @abstractmethod
    def off(self) -> None:
        """
        Turn device off or deactivate it.
        
        Raises:
            DeviceError: If operation fails
        """
        pass
    
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Get current device status.
        
        Returns:
            Dictionary containing device state
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get cached device state.
        
        Returns:
            Current state dictionary
        """
        return self._state.copy()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}', pin={self.pin})"