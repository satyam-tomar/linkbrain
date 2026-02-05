"""
Tool registry for AI-executable actions.
"""

import logging
from typing import Dict, Any, Optional, List

from linkbrain_core.tools.base import BaseToolDevice
from linkbrain_core.parsers.action_parser import DeviceAction

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for AI-executable tools.
    """

    def __init__(self):
        self.devices: Dict[str, BaseToolDevice] = {}
        logger.info("Tool registry initialized")

    def register_device(self, name: str, device: BaseToolDevice) -> None:
        self.devices[name] = device
        logger.info(f"Registered tool: {name}")

    def get_device(self, name: str) -> Optional[BaseToolDevice]:
        return self.devices.get(name)

    def list_devices(self) -> Dict[str, set[str]]:
        return {
            name: device.supported_actions()
            for name, device in self.devices.items()
        }

    async def execute_action(self, action: DeviceAction) -> Dict[str, Any]:
        device = self.get_device(action.device)

        if not device:
            return {
                "success": False,
                "error": f"Device '{action.device}' not found"
            }

        if action.action not in device.supported_actions():
            return {
                "success": False,
                "error": f"Action '{action.action}' not supported"
            }

        try:
            method = getattr(device, action.action)
            result = await method()

            if action.action == "status":
                return {
                    "success": True,
                    "device": action.device,
                    "data": result
                }

            return {
                "success": True,
                "device": action.device,
                "action": action.action
            }

        except Exception as e:
            logger.exception("Tool execution failed")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_actions(self, actions: List[DeviceAction]) -> List[Dict[str, Any]]:
        return [await self.execute_action(a) for a in actions]