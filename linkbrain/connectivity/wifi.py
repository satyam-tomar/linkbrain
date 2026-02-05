"""
Wi-Fi connectivity implementation for ESP32.

Communicates with ESP32 over Wi-Fi using TCP sockets.
"""

import socket
import time
from typing import Optional
import logging

from linkbrain.connectivity.base import BaseConnectivity
from linkbrain.core.command import Command, CommandResponse, CommandType
from linkbrain.core.exceptions import ConnectionError, CommandError, TimeoutError

logger = logging.getLogger(__name__)

__all__ = ['WiFiConnectivity']


class WiFiConnectivity(BaseConnectivity):
    """
    Wi-Fi (TCP/IP) connectivity implementation for ESP32.
    
    Communicates with ESP32 over Wi-Fi using TCP sockets.
    
    Example:
        >>> wifi = WiFiConnectivity(device_address="192.168.1.100", port=8080)
        >>> wifi.connect()
        >>> response = wifi.send_command(Command.status())
        >>> wifi.disconnect()
    """
    
    def __init__(
        self,
        device_address: str,
        port: int = 8080,
        timeout: float = 5.0
    ):
        """
        Initialize Wi-Fi connectivity.
        
        Args:
            device_address: IP address of ESP32 (e.g., "192.168.1.100")
            port: TCP port for communication
            timeout: Connection timeout in seconds
        """
        super().__init__(device_address, timeout)
        self.port = port
        self._socket: Optional[socket.socket] = None
        logger.info(
            f"Wi-Fi connectivity initialized for {device_address}:{port}"
        )
    
    def connect(self) -> None:
        """
        Establish Wi-Fi connection to ESP32.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(
                f"Connecting to ESP32 via Wi-Fi at "
                f"{self.device_address}:{self.port}"
            )
            
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            
            # Connect to ESP32
            self._socket.connect((self.device_address, self.port))
            
            self._connected = True
            logger.info("Wi-Fi connection established")
            
        except socket.timeout:
            raise ConnectionError(f"Connection timed out after {self.timeout}s")
        except socket.error as e:
            raise ConnectionError(f"Failed to connect via Wi-Fi: {str(e)}")
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect via Wi-Fi: {str(e)}")
    
    def disconnect(self) -> None:
        """Disconnect from ESP32."""
        if self._socket:
            try:
                self._socket.close()
                logger.info("Wi-Fi disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self._socket = None
                self._connected = False
        else:
            self._connected = False
    
    def send_command(self, command: Command) -> CommandResponse:
        """
        Send command via Wi-Fi.
        
        Args:
            command: Command to send
        
        Returns:
            Response from ESP32
        
        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
            TimeoutError: If command times out
        """
        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to ESP32")
        
        try:
            # Convert command to protocol string
            cmd_string = command.to_protocol_string()
            logger.debug(f"Sending command: {cmd_string}")
            
            # Send via socket
            self._socket.sendall(cmd_string.encode('utf-8') + b'\n')
            
            # Receive response
            response_data = self._receive_response()
            
            response = CommandResponse.from_string(response_data)
            logger.debug(f"Received response: {response}")
            
            return response
            
        except socket.timeout:
            raise TimeoutError(f"Command timed out after {command.timeout}s")
        except socket.error as e:
            raise CommandError(f"Socket error: {str(e)}")
        except Exception as e:
            raise CommandError(f"Command failed: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected and self._socket is not None
    
    def _receive_response(self, buffer_size: int = 4096) -> str:
        """
        Receive response from ESP32.
        
        Args:
            buffer_size: Size of receive buffer
        
        Returns:
            Response string
        
        Raises:
            CommandError: If receive fails
        """
        try:
            data = self._socket.recv(buffer_size)
            if not data:
                raise CommandError("Connection closed by ESP32")
            return data.decode('utf-8').strip()
        except socket.timeout:
            raise TimeoutError("Response timeout")
        except Exception as e:
            raise CommandError(f"Failed to receive response: {e}")