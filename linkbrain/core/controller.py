"""
Main ESP32 controller - central entry point for device communication.
"""

from typing import Optional, Dict, Any
from linkbrain.connectivity.base import BaseConnectivity
from linkbrain.connectivity.bluetooth import BluetoothConnectivity
from linkbrain.connectivity.wifi import WiFiConnectivity
from linkbrain.core.command import Command, CommandResponse
from linkbrain.core.exceptions import UnsupportedModeError, ConnectionError
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class ESP32Controller:
    """
    Main controller for ESP32 communication.
    
    This is the single entry point for all ESP32 interactions. It manages
    connectivity and dispatches commands to the ESP32 device.
    
    Devices should communicate exclusively through this controller,
    never directly managing connectivity.
    
    Example:
        >>> controller = ESP32Controller(mode="bluetooth", device_address="AA:BB:CC:DD:EE:FF")
        >>> controller.connect()
        >>> response = controller.send_command(Command.gpio_set(12, 1))
        >>> controller.disconnect()
    """
    
    SUPPORTED_MODES = ["bluetooth", "wifi"]
    
    def __init__(
        self,
        mode: str = "bluetooth",
        device_address: Optional[str] = None,
        port: int = 8080,
        timeout: float = 5.0,
        **kwargs
    ):
        """
        Initialize ESP32 controller.
        
        Args:
            mode: Connectivity mode ("bluetooth" or "wifi")
            device_address: Device address (MAC for BT, IP for Wi-Fi)
            port: Port number (for Wi-Fi mode only)
            timeout: Default timeout for operations
            **kwargs: Additional connectivity-specific parameters
        
        Raises:
            UnsupportedModeError: If mode is not supported
            ValueError: If required parameters are missing
        """
        if mode not in self.SUPPORTED_MODES:
            raise UnsupportedModeError(
                f"Mode '{mode}' not supported. Use one of: {self.SUPPORTED_MODES}"
            )
        
        if device_address is None:
            raise ValueError("device_address is required")
        
        self.mode = mode
        self.device_address = device_address
        self.timeout = timeout
        
        # Initialize appropriate connectivity
        self._connectivity: BaseConnectivity = self._create_connectivity(
            mode, device_address, port, timeout, **kwargs
        )
        
        logger.info(f"ESP32Controller initialized with {mode} mode")
    
    def _create_connectivity(
        self,
        mode: str,
        device_address: str,
        port: int,
        timeout: float,
        **kwargs
    ) -> BaseConnectivity:
        """
        Factory method to create connectivity instance.
        
        Args:
            mode: Connectivity mode
            device_address: Device address
            port: Port number
            timeout: Timeout value
            **kwargs: Additional parameters
        
        Returns:
            Connectivity instance
        """
        if mode == "bluetooth":
            return BluetoothConnectivity(device_address, timeout)
        elif mode == "wifi":
            return WiFiConnectivity(device_address, port, timeout)
        else:
            raise UnsupportedModeError(f"Unknown mode: {mode}")
    
    def connect(self) -> None:
        """
        Connect to the ESP32 device.
        
        Raises:
            ConnectionError: If connection fails
        """
        logger.info(f"Connecting to ESP32 at {self.device_address}")
        self._connectivity.connect()
        logger.info("Successfully connected to ESP32")
    
    def disconnect(self) -> None:
        """Disconnect from the ESP32 device."""
        logger.info("Disconnecting from ESP32")
        self._connectivity.disconnect()
    
    def send_command(self, command: Command) -> CommandResponse:
        """
        Send a command to the ESP32.
        
        Args:
            command: Command to send
        
        Returns:
            Response from ESP32
        
        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
            TimeoutError: If command times out
        """
        return self._connectivity.send_command(command)
    
    def is_connected(self) -> bool:
        """
        Check if connected to ESP32.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connectivity.is_connected()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get ESP32 device status.
        
        Returns:
            Dictionary containing device status information
        
        Raises:
            ConnectionError: If not connected
        """
        response = self.send_command(Command.status())
        if response.success:
            return response.data
        else:
            return {"status": "error", "message": response.error}
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
    
    def __repr__(self) -> str:
        status = "connected" if self.is_connected() else "disconnected"
        return f"ESP32Controller(mode={self.mode}, address={self.device_address}, status={status})"