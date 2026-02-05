"""
Custom exceptions for the LinkBrain SDK.

These exceptions cover hardware communication, connectivity,
and device control errors.
"""


class LinkBrainError(Exception):
    """Base exception for all LinkBrain SDK errors."""
    pass


class ConnectionError(LinkBrainError):
    """
    Raised when connection to ESP32 fails or is lost.
    
    Examples:
        - Bluetooth device not found
        - WiFi connection timeout
        - Connection dropped during operation
    """
    pass


class CommandError(LinkBrainError):
    """
    Raised when a command fails to execute or is invalid.
    
    Examples:
        - Invalid command format
        - ESP32 rejected command
        - Command execution failed
    """
    pass


class DeviceError(LinkBrainError):
    """
    Raised when a device operation fails.
    
    Examples:
        - Device not initialized
        - Invalid device state
        - Hardware malfunction
    """
    pass


class TimeoutError(LinkBrainError):
    """
    Raised when an operation times out.
    
    Examples:
        - Command response timeout
        - Connection timeout
        - Device response timeout
    """
    pass


class InvalidPinError(LinkBrainError):
    """
    Raised when an invalid GPIO pin is specified.
    
    Examples:
        - Pin number out of range
        - Reserved pin used
        - Pin not configured for requested mode
    """
    pass


class UnsupportedModeError(LinkBrainError):
    """
    Raised when an unsupported connectivity mode is requested.
    
    Examples:
        - Invalid connectivity mode
        - Mode not available on platform
    """
    pass