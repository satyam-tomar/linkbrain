"""
Base connectivity interface for ESP32 communication.

All connectivity implementations (Bluetooth, Wi-Fi, etc.) must
inherit from BaseConnectivity and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

from linkbrain.core.command import Command, CommandResponse
from linkbrain.core.exceptions import ConnectionError, CommandError, TimeoutError

logger = logging.getLogger(__name__)

__all__ = ['BaseConnectivity']


class BaseConnectivity(ABC):
    """
    Abstract base class for ESP32 connectivity implementations.
    
    All connectivity modes (Bluetooth, Wi-Fi, etc.) must inherit from this
    class and implement the required methods.
    """
    
    def __init__(self, device_address: str, timeout: float = 5.0):
        """
        Initialize connectivity.
        
        Args:
            device_address: Address of the ESP32 device (MAC for BT, IP for Wi-Fi)
            timeout: Default timeout for operations in seconds
        """
        self.device_address = device_address
        self.timeout = timeout
        self._connected = False
        logger.debug(
            f"Initialized {self.__class__.__name__} for {device_address}"
        )
    
    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the ESP32 device.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the ESP32 device.
        """
        pass
    
    @abstractmethod
    def send_command(self, command: Command) -> CommandResponse:
        """
        Send a command to the ESP32 and receive response.
        
        Args:
            command: Command to send
        
        Returns:
            Response from the ESP32
        
        Raises:
            ConnectionError: If not connected
            CommandError: If command execution fails
            TimeoutError: If command times out
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if currently connected to the device.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
    
    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self._connected else "disconnected"
        return f"{self.__class__.__name__}({self.device_address}, {status})"