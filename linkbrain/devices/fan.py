from typing import Dict, Any
import logging
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import DeviceError

logger = logging.getLogger(__name__)
__all__ = ['Fan']

class Fan(BaseDevice):
    """Fan device controller."""
    
    def __init__(self, name: str, controller: ESP32Controller, pin: int):
        super().__init__(name, controller, pin)
        self._state = {"power": "off", "pin": pin}
    
    def on(self) -> None:
        """Turn fan on."""
        try:
            logger.info(f"Turning on fan '{self.name}'")
            response = self.controller.send_command(Command.gpio_set(self.pin, 1))
            if not response.success:
                raise DeviceError(f"Failed: {response.error}")
            self._state["power"] = "on"
        except Exception as e:
            raise DeviceError(f"Failed to turn on fan: {e}")
    
    def off(self) -> None:
        """Turn fan off."""
        try:
            logger.info(f"Turning off fan '{self.name}'")
            response = self.controller.send_command(Command.gpio_set(self.pin, 0))
            if not response.success:
                raise DeviceError(f"Failed: {response.error}")
            self._state["power"] = "off"
        except Exception as e:
            raise DeviceError(f"Failed to turn off fan: {e}")
    
    def status(self) -> Dict[str, Any]:
        """Get fan status."""
        return self.get_state()
