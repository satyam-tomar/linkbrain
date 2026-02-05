

from typing import Dict, Any
import logging
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import DeviceError

logger = logging.getLogger(__name__)
__all__ = ['Door']

class Door(BaseDevice):
    """Door lock controller."""
    
    def __init__(self, name: str, controller: ESP32Controller, pin: int):
        super().__init__(name, controller, pin)
        self._state = {"lock_state": "locked", "pin": pin}
    
    def on(self) -> None:
        """Unlock door."""
        self.unlock()
    
    def off(self) -> None:
        """Lock door."""
        self.lock()
    
    def lock(self) -> None:
        """Lock the door."""
        try:
            logger.info(f"Locking door '{self.name}'")
            response = self.controller.send_command(Command.gpio_set(self.pin, 0))
            if not response.success:
                raise DeviceError(f"Failed: {response.error}")
            self._state["lock_state"] = "locked"
        except Exception as e:
            raise DeviceError(f"Failed to lock door: {e}")
    
    def unlock(self) -> None:
        """Unlock the door."""
        try:
            logger.info(f"Unlocking door '{self.name}'")
            response = self.controller.send_command(Command.gpio_set(self.pin, 1))
            if not response.success:
                raise DeviceError(f"Failed: {response.error}")
            self._state["lock_state"] = "unlocked"
        except Exception as e:
            raise DeviceError(f"Failed to unlock door: {e}")
    
    def status(self) -> Dict[str, Any]:
        """Get door status."""
        return self.get_state()