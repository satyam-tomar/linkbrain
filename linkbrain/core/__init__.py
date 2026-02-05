"""
LinkBrain Core Module.

Provides core functionality for ESP32 communication including
controllers, commands, and exceptions.
"""

from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command, CommandResponse, CommandType
from linkbrain.core.exceptions import (
    LinkBrainError,
    ConnectionError,
    CommandError,
    DeviceError,
    TimeoutError,
    InvalidPinError,
    UnsupportedModeError
)

__all__ = [
    # Controller
    'ESP32Controller',
    
    # Commands
    'Command',
    'CommandResponse',
    'CommandType',
    
    # Exceptions
    'LinkBrainError',
    'ConnectionError',
    'CommandError',
    'DeviceError',
    'TimeoutError',
    'InvalidPinError',
    'UnsupportedModeError',
]