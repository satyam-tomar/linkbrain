"""
Command abstraction for ESP32 communication protocol.

This module defines the command protocol used to communicate
with ESP32 devices, including command types, serialization,
and response parsing.
"""

from typing import Dict, Any, Optional
from enum import Enum

__all__ = ['CommandType', 'Command', 'CommandResponse']


class CommandType(Enum):
    """Enumeration of supported command types."""
    GPIO_SET = "gpio_set"
    GPIO_GET = "gpio_get"
    GPIO_MODE = "gpio_mode"
    STATUS = "status"
    RESET = "reset"


class Command:
    """
    Represents a command to be sent to the ESP32.
    
    Commands follow a simple protocol format that can be serialized
    to JSON or other formats for transmission.
    """
    
    def __init__(
        self,
        cmd_type: CommandType,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0
    ):
        """
        Initialize a command.
        
        Args:
            cmd_type: The type of command to execute
            params: Dictionary of command parameters
            timeout: Command timeout in seconds
        """
        self.cmd_type = cmd_type
        self.params = params or {}
        self.timeout = timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize command to dictionary format.
        
        Returns:
            Dictionary representation of the command
        """
        return {
            "type": self.cmd_type.value,
            "params": self.params,
            "timeout": self.timeout
        }
    
    def to_protocol_string(self) -> str:
        """
        Convert command to protocol string for transmission.
        
        Format: TYPE:PARAM1=VALUE1,PARAM2=VALUE2
        Example: gpio_set:pin=12,value=1
        
        Returns:
            Protocol-formatted string
        """
        if not self.params:
            return self.cmd_type.value
        
        param_str = ",".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.cmd_type.value}:{param_str}"
    
    @staticmethod
    def gpio_set(pin: int, value: int) -> 'Command':
        """
        Create a GPIO set command.
        
        Args:
            pin: GPIO pin number
            value: Pin value (0 or 1)
        
        Returns:
            Command instance
        """
        return Command(
            CommandType.GPIO_SET,
            {"pin": pin, "value": value}
        )
    
    @staticmethod
    def gpio_get(pin: int) -> 'Command':
        """
        Create a GPIO get command.
        
        Args:
            pin: GPIO pin number
        
        Returns:
            Command instance
        """
        return Command(
            CommandType.GPIO_GET,
            {"pin": pin}
        )
    
    @staticmethod
    def gpio_mode(pin: int, mode: str) -> 'Command':
        """
        Create a GPIO mode configuration command.
        
        Args:
            pin: GPIO pin number
            mode: Pin mode ("input", "output", "input_pullup")
        
        Returns:
            Command instance
        """
        return Command(
            CommandType.GPIO_MODE,
            {"pin": pin, "mode": mode}
        )
    
    @staticmethod
    def status() -> 'Command':
        """
        Create a status query command.
        
        Returns:
            Command instance
        """
        return Command(CommandType.STATUS)
    
    def __repr__(self) -> str:
        return f"Command({self.cmd_type.value}, {self.params})"


class CommandResponse:
    """Represents a response from the ESP32."""
    
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Initialize a command response.
        
        Args:
            success: Whether the command succeeded
            data: Response data
            error: Error message if command failed
        """
        self.success = success
        self.data = data or {}
        self.error = error
    
    @staticmethod
    def from_string(response_str: str) -> 'CommandResponse':
        """
        Parse a response string from ESP32.
        
        Format: OK:key1=value1,key2=value2 or ERROR:message
        
        Args:
            response_str: Raw response string
        
        Returns:
            CommandResponse instance
        """
        if response_str.startswith("OK"):
            parts = response_str.split(":", 1)
            data = {}
            if len(parts) > 1 and parts[1]:
                for pair in parts[1].split(","):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        data[key.strip()] = value.strip()
            return CommandResponse(success=True, data=data)
        elif response_str.startswith("ERROR"):
            error_msg = response_str.split(":", 1)[1] if ":" in response_str else "Unknown error"
            return CommandResponse(success=False, error=error_msg)
        else:
            return CommandResponse(success=False, error=f"Invalid response format: {response_str}")
    
    def __repr__(self) -> str:
        if self.success:
            return f"CommandResponse(success=True, data={self.data})"
        else:
            return f"CommandResponse(success=False, error={self.error})"