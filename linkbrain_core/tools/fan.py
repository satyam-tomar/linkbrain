# linkbrain_tools/fan_tool.py

from typing import Dict, Any
from tools.base import BaseToolDevice
from linkbrain.devices.fan import Fan


class FanTool(BaseToolDevice):
    def __init__(self, name: str, fan: Fan):
        super().__init__(name)
        self.fan = fan

    async def on(self) -> None:
        self.fan.on()

    async def off(self) -> None:
        self.fan.off()

    async def status(self) -> Dict[str, Any]:
        return self.fan.status()

    def supported_actions(self) -> set[str]:
        return {"on", "off", "status"}
