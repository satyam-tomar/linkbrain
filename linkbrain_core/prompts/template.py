"""
Prompt builder for LinkBrain Core.

Builds structured prompts for LLM providers with device context.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

__all__ = ['DeviceContext', 'PromptBuilder']


@dataclass
class DeviceContext:
    """Device information for LLM context."""
    name: str
    device_type: str
    current_state: str
    available_actions: Set[str]
    metadata: Optional[Dict] = None


class PromptBuilder:
    """
    Builds structured prompts for LLM providers.
    
    Translates device registry state into LLM-readable context
    and constructs prompts that elicit valid JSON responses.
    """

    SYSTEM_TEMPLATE = """You are a smart home assistant controlling ESP32 devices through LinkBrain.

Available Devices:
{device_list}

Your task:
1. Understand the user's natural language request
2. Identify which devices to control
3. Determine the appropriate action for each device
4. Respond ONLY with valid JSON
5. Respond in the same language user gives you the request. 

Response Format (strict):
{{
  "actions": [
    {{"device": "device_name", "action": "action_name"}}
  ],
  "message": "Brief confirmation message"
}}

Rules:
-  if user ask somethiing out of the given things then reply the related things to hiim directly in two lines and don't write extra about home appicancies in that case. 
- Only use devices from the available list
- Only use actions listed for each device
- If device name is ambiguous, use closest match
- If request is impossible, return empty actions array with explanation
- Always return valid, parseable JSON
- Do not include markdown formatting"""

    def __init__(self):
        """Initialize prompt builder."""
        self.devices: Dict[str, DeviceContext] = {}

    def register_device(self, context: DeviceContext) -> None:
        """
        Register device for prompt context.
        
        Args:
            context: Device context information
        """
        self.devices[context.name] = context

    def unregister_device(self, name: str) -> None:
        """Remove device from context."""
        self.devices.pop(name, None)

    def clear_devices(self) -> None:
        """Clear all registered devices."""
        self.devices.clear()

    def build_device_list(self) -> str:
        """
        Build formatted device list for LLM context.
        
        Returns:
            Formatted multi-line device list
        """
        if not self.devices:
            return "No devices registered"
        
        lines = []
        for name, ctx in self.devices.items():
            actions_str = ", ".join(sorted(ctx.available_actions))
            lines.append(
                f"- {name}: {ctx.device_type} "
                f"(state: {ctx.current_state}, actions: {actions_str})"
            )
        
        return "\n".join(lines)

    def build_prompt(
        self,
        user_input: str,
        include_system: bool = True
    ) -> str:
        """
        Build complete prompt for LLM.
        
        Args:
            user_input: User's natural language request
            include_system: Include system prompt (default: True)
        
        Returns:
            Complete prompt string
        """
        device_list = self.build_device_list()
        
        if include_system:
            system_prompt = self.SYSTEM_TEMPLATE.format(
                device_list=device_list
            )
            return f"{system_prompt}\n\nUser Request: {user_input}\n\nJSON Response:"
        else:
            return f"Devices:\n{device_list}\n\nRequest: {user_input}"

    def get_device_count(self) -> int:
        """Get number of registered devices."""
        return len(self.devices)