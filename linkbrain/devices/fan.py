"""
Fan device implementation.
"""

from typing import Dict, Any, Optional
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class Fan(BaseDevice):
    """
    Fan device controlled by ESP32.
    
    Controls a fan connected to a GPIO pin via relay or transistor.
    
    Example:
        >>> fan = Fan(controller, pin=12, name="Living Room Fan")
        >>> fan.on()
        >>> fan.status()
        {'name': 'Living Room Fan', 'pin': 12, 'state': 'on'}
        >>> fan.off()
    """
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None
    ):
        """
        Initialize fan device.
        
        Args:
            controller: ESP32Controller instance
            pin: GPIO pin number
            name: Optional fan name
        """
        super().__init__(controller, pin, name)
        self._is_on = False
    
    def on(self) -> None:
        """
        Turn the fan on.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Turning on {self.name}")
        self._set_pin(1)
        self._is_on = True
    
    def off(self) -> None:
        """
        Turn the fan off.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Turning off {self.name}")
        self._set_pin(0)
        self._is_on = False
    
    def toggle(self) -> None:
        """Toggle fan state (on ↔ off)."""
        if self._is_on:
            self.off()
        else:
            self.on()
    
    def status(self) -> Dict[str, Any]:
        """
        Get fan status.
        
        Returns:
            Dictionary with fan status information
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
            "type": "fan"
        }