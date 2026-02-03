"""
Light device implementation.
"""

from typing import Dict, Any, Optional
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class Light(BaseDevice):
    """
    Light device controlled by ESP32.
    
    Controls a light (LED, bulb, etc.) connected to a GPIO pin.
    
    Example:
        >>> light = Light(controller, pin=14, name="Bedroom Light")
        >>> light.on()
        >>> light.off()
    """
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None
    ):
        """
        Initialize light device.
        
        Args:
            controller: ESP32Controller instance
            pin: GPIO pin number
            name: Optional light name
        """
        super().__init__(controller, pin, name)
        self._is_on = False
    
    def on(self) -> None:
        """
        Turn the light on.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Turning on {self.name}")
        self._set_pin(1)
        self._is_on = True
    
    def off(self) -> None:
        """
        Turn the light off.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Turning off {self.name}")
        self._set_pin(0)
        self._is_on = False
    
    def toggle(self) -> None:
        """Toggle light state (on ↔ off)."""
        if self._is_on:
            self.off()
        else:
            self.on()
    
    def status(self) -> Dict[str, Any]:
        """
        Get light status.
        
        Returns:
            Dictionary with light status information
        """
        try:
            current_value = self._get_pin()
            self._is_on = bool(current_value)
        except Exception as e:
            logger.warning(f"Could not read pin status: {e}")
        
        return {
            "name": self.name,
            "pin": self.pin,
            "state": "on" if self._is_on else "off",
            "type": "light"
        }