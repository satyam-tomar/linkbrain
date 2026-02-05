"""Light tool wrapper."""

from typing import Dict, Any
from linkbrain_core.tools.base import BaseToolDevice
from linkbrain.devices.light import Light

__all__ = ['LightTool']


class LightTool(BaseToolDevice):
    """AI-executable light tool."""
    
    def __init__(self, name: str, light: Light):
        super().__init__(name)
        self.light = light

    async def on(self) -> None:
        self.light.on()

    async def off(self) -> None:
        self.light.off()

    async def status(self) -> Dict[str, Any]:
        return self.light.status()

    def supported_actions(self) -> set[str]:
        return {"on", "off", "status"}