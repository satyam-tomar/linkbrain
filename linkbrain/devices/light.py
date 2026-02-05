"""
Light device implementation.
"""

from typing import Dict, Any
import logging

from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import DeviceError

logger = logging.getLogger(__name__)

__all__ = ['Light']


class Light(BaseDevice):
    """
    Light device controller.
    
    Controls a light connected to an ESP32 GPIO pin.
    
    Example:
        >>> controller = ESP32Controller(mode="bluetooth")
        >>> controller.connect()
        >>> light = Light("Living Room", controller, pin=12)
        >>> light.on()
        >>> light.off()
        >>> status = light.status()
    """
    
    def __init__(
        self,
        name: str,
        controller: ESP32Controller,
        pin: int
    ):
        """
        Initialize light device.
        
        Args:
            name: Human-readable light name
            controller: ESP32 controller instance
            pin: GPIO pin number
        """
        super().__init__(name, controller, pin)
        self._state = {"power": "off", "pin": pin}
    
    def on(self) -> None:
        """
        Turn light on.
        
        Raises:
            DeviceError: If operation fails
        """
        try:
            logger.info(f"Turning on light '{self.name}' (pin {self.pin})")
            command = Command.gpio_set(self.pin, 1)
            response = self.controller.send_command(command)
            
            if not response.success:
                raise DeviceError(f"Failed to turn on light: {response.error}")
            
            self._state["power"] = "on"
            logger.info(f"Light '{self.name}' is now on")
            
        except Exception as e:
            raise DeviceError(f"Failed to turn on light: {e}")
    
    def off(self) -> None:
        """
        Turn light off.
        
        Raises:
            DeviceError: If operation fails
        """
        try:
            logger.info(f"Turning off light '{self.name}' (pin {self.pin})")
            command = Command.gpio_set(self.pin, 0)
            response = self.controller.send_command(command)
            
            if not response.success:
                raise DeviceError(f"Failed to turn off light: {response.error}")
            
            self._state["power"] = "off"
            logger.info(f"Light '{self.name}' is now off")
            
        except Exception as e:
            raise DeviceError(f"Failed to turn off light: {e}")
    
    def status(self) -> Dict[str, Any]:
        """
        Get light status.
        
        Returns:
            Dictionary with light state
        """
        try:
            command = Command.gpio_get(self.pin)
            response = self.controller.send_command(command)
            
            if response.success and "value" in response.data:
                value = int(response.data["value"])
                self._state["power"] = "on" if value == 1 else "off"
            
            return self.get_state()
            
        except Exception as e:
            logger.error(f"Failed to get light status: {e}")
            return self.get_state()