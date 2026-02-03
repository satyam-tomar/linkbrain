"""
Custom exceptions for the ESP32X SDK.
"""


class LinkBrainError(Exception):
    """Base exception for all ESP32X SDK errors."""
    pass


class ConnectionError(LinkBrainError):
    """Raised when connection to ESP32 fails or is lost."""
    pass


class CommandError(LinkBrainError):
    """Raised when a command fails to execute or is invalid."""
    pass


class DeviceError(LinkBrainError):
    """Raised when a device operation fails."""
    pass


class TimeoutError(LinkBrainError):
    """Raised when an operation times out."""
    pass


class InvalidPinError(LinkBrainError):
    """Raised when an invalid GPIO pin is specified."""
    pass


class UnsupportedModeError(LinkBrainError):
    """Raised when an unsupported connectivity mode is requested."""
    pass