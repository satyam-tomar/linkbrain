# linkbrain_tools/light_tool.py

from typing import Dict, Any
from tools.base import BaseToolDevice
from linkbrain.devices.light import Light


class LightTool(BaseToolDevice):
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
