
"""Door tool wrapper."""

from typing import Dict, Any
from linkbrain_core.tools.base import BaseToolDevice
from linkbrain.devices.door import Door

__all__ = ['DoorTool']


class DoorTool(BaseToolDevice):
    """AI-executable door tool."""
    
    def __init__(self, name: str, door: Door):
        super().__init__(name)
        self.door = door

    async def on(self) -> None:
        self.door.unlock()

    async def off(self) -> None:
        self.door.lock()

    async def status(self) -> Dict[str, Any]:
        return self.door.status()

    def supported_actions(self) -> set[str]:
        return {"on", "off", "status", "lock", "unlock"}
