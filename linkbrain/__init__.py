"""
from linkbrain.core.controller import ESP32ControllerLinkBrain - ESP32 Home Automation Control SDK
===========================================

A clean, extensible Python library for controlling ESP32-based home automation devices.

Example Usage:
    >>> from LinkBrain import ESP32Controller
    >>> from LinkBrain.devices import Fan, Light
    >>> 
    >>> controller = ESP32Controller(mode="bluetooth", device_address="AA:BB:CC:DD:EE:FF")
    >>> controller.connect()
    >>> 
    >>> fan = Fan(controller, pin=12)
    >>> light = Light(controller, pin=14)
    >>> 
    >>> fan.on()
    >>> light.off()
    >>> controller.disconnect()
"""

__version__ = "0.1.0"
__author__ = "LinkBrain Development Team"

from linkbrain.core.controller import ESP32Controller

from linkbrain.core.exceptions import (
    LinkBrainError,
    ConnectionError,
    CommandError,
    DeviceError,
    TimeoutError
)

__all__ = [
    "ESP32Controller",
    "LinkBrainError",
    "ConnectionError",
    "CommandError",
    "DeviceError",
    "TimeoutError",
]