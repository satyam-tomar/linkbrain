"""
Door controller device implementation.
"""

from typing import Dict, Any, Optional
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class Door(BaseDevice):
    """
    Door controller device controlled by ESP32.
    
    Controls an automated door lock or actuator via GPIO pin.
    Common use cases: smart locks, garage doors, automatic doors.
    
    Example:
        >>> door = Door(controller, pin=16, name="Front Door")
        >>> door.unlock()
        >>> door.status()
        {'name': 'Front Door', 'pin': 16, 'state': 'unlocked'}
        >>> door.lock()
    """
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None
    ):
        """
        Initialize door controller.
        
        Args:
            controller: ESP32Controller instance
            pin: GPIO pin number
            name: Optional door name
        """
        super().__init__(controller, pin, name)
        self._is_locked = True
        # Start in locked position for safety
        self.lock()
    
    def lock(self) -> None:
        """
        Lock the door.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Locking {self.name}")
        self._set_pin(0)  # 0 = locked
        self._is_locked = True
    
    def unlock(self) -> None:
        """
        Unlock the door.
        
        Raises:
            DeviceError: If operation fails
        """
        logger.info(f"Unlocking {self.name}")
        self._set_pin(1)  # 1 = unlocked
        self._is_locked = False
    
    def toggle(self) -> None:
        """Toggle door state (locked ↔ unlocked)."""
        if self._is_locked:
            self.unlock()
        else:
            self.lock()
    
    def status(self) -> Dict[str, Any]:
        """
        Get door status.
        
        Returns:
            Dictionary with door status information
        """
        try:
            current_value = self._get_pin()
            self._is_locked = not bool(current_value)
        except Exception as e:
            logger.warning(f"Could not read pin status: {e}")
        
        return {
            "name": self.name,
            "pin": self.pin,
            "state": "locked" if self._is_locked else "unlocked",
            "type": "door"
        }