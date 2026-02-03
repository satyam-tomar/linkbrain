"""
Base device class for all ESP32-controlled devices.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import InvalidPinError, DeviceError
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class BaseDevice(ABC):
    """
    Abstract base class for ESP32-controlled devices.
    
    All devices (Fan, Light, Door, etc.) inherit from this class.
    Devices communicate with ESP32 exclusively through the controller.
    """
    
    # Valid GPIO pins for ESP32
    VALID_PINS = list(range(0, 40))
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None
    ):
        """
        Initialize a device.
        
        Args:
            controller: ESP32Controller instance for communication
            pin: GPIO pin number connected to this device
            name: Optional device name for identification
        
        Raises:
            InvalidPinError: If pin number is invalid
        """
        if pin not in self.VALID_PINS:
            raise InvalidPinError(
                f"Invalid pin {pin}. Valid pins: {self.VALID_PINS}"
            )
        
        self.controller = controller
        self.pin = pin
        self.name = name or f"{self.__class__.__name__}_{pin}"
        self._state: Dict[str, Any] = {}
        
        # Initialize GPIO pin as output
        self._initialize_pin()
        
        logger.info(f"{self.name} initialized on pin {pin}")
    
    def _initialize_pin(self) -> None:
        """Initialize the GPIO pin as output."""
        try:
            command = Command.gpio_mode(self.pin, "output")
            response = self.controller.send_command(command)
            if not response.success:
                logger.warning(f"Failed to initialize pin {self.pin}: {response.error}")
        except Exception as e:
            logger.warning(f"Could not initialize pin {self.pin}: {e}")
    
    def _set_pin(self, value: int) -> None:
        """
        Set the GPIO pin value.
        
        Args:
            value: Pin value (0 or 1)
        
        Raises:
            DeviceError: If operation fails
        """
        try:
            command = Command.gpio_set(self.pin, value)
            response = self.controller.send_command(command)
            
            if not response.success:
                raise DeviceError(f"Failed to set pin {self.pin}: {response.error}")
            
            self._state["pin_value"] = value
            logger.debug(f"{self.name} pin set to {value}")
            
        except Exception as e:
            raise DeviceError(f"Error setting pin {self.pin}: {str(e)}")
    
    def _get_pin(self) -> int:
        """
        Get the current GPIO pin value.
        
        Returns:
            Current pin value (0 or 1)
        
        Raises:
            DeviceError: If operation fails
        """
        try:
            command = Command.gpio_get(self.pin)
            response = self.controller.send_command(command)
            
            if not response.success:
                raise DeviceError(f"Failed to get pin {self.pin}: {response.error}")
            
            value = int(response.data.get("value", 0))
            self._state["pin_value"] = value
            return value
            
        except Exception as e:
            raise DeviceError(f"Error reading pin {self.pin}: {str(e)}")
    
    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Get device status.
        
        Returns:
            Dictionary containing device status information
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, pin={self.pin})"