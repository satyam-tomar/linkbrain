"""
Window controller device implementation.
"""

from typing import Dict, Any, Optional
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class Window(BaseDevice):
    """
    Window controller device controlled by ESP32.
    
    Controls automated window blinds, shutters, or actuators via GPIO pin.
    
    Example:
        >>> window = Window(controller, pin=18, name="Living Room Window")
        >>> window.open()
        >>> window.close()
    """
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None
    ):
        """
        Initialize window controller.
        
        Args:
            controller: ESP32Controller instance
            pin: GPIO pin number
            name: Optional window name
        """
        super().__init__(controller, pin, name)
        self._is_open = False
    
    def open(self) -> None:
        """
        Open the window (or blinds/shutters).
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Opening {self.name}")
        self._set_pin(1)  # 1 = open
        self._is_open = True
    
    def close(self) -> None:
        """
        Close the window (or blinds/shutters).
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Closing {self.name}")
        self._set_pin(0)  # 0 = closed
        self._is_open = False
    
    def toggle(self) -> None:
        """Toggle window state (open ↔ closed)."""
        if self._is_open:
            self.close()
        else:
            self.open()
    
    def status(self) -> Dict[str, Any]:
        """
        Get window status.
        
        Returns:
            Dictionary with window status information
        """
        try:
            current_value = self._get_pin()
            self._is_open = bool(current_value)
        except Exception as e:
            logger.warning(f"Could not read pin status: {e}")
        
        return {
            "name": self.name,
            "pin": self.pin,
            "state": "open" if self._is_open else "closed",
            "type": "window"
        }