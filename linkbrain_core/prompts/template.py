"""
Prompt template system for smart home AI assistant.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """Information about a registered device."""
    name: str
    device_type: str
    current_state: str
    available_actions: List[str]


class PromptTemplate:
    """
    Builds structured prompts for LLM with device context.
    """
    
    SYSTEM_PROMPT = """You are a smart home assistant controlling ESP32 devices via Python code.

Available Devices:
{device_list}

Your task:
1. Understand the user's natural language request
2. Identify which devices to control
3. Determine the action for each device
4. Respond ONLY with valid JSON

Response Format (strict):
{{
  "actions": [
    {{"device": "device_name", "action": "on|off|status"}}
  ],
  "message": "Brief confirmation message"
}}

Rules:
- Only use devices from the available list
- Only use actions: "on", "off", "status"
- If device name is unclear, use closest match
- If request is impossible, return empty actions array with explanation in message
- Always return valid JSON"""
    
    def __init__(self):
        """Initialize prompt template."""
        self.devices: Dict[str, DeviceInfo] = {}
    
    def register_device(self, device_info: DeviceInfo) -> None:
        """
        Register device for prompt context.
        
        Args:
            device_info: Device information
        """
        self.devices[device_info.name] = device_info
    
    def build_device_list(self) -> str:
        """
        Build formatted device list for prompt.
        
        Returns:
            Formatted device list string
        """
        if not self.devices:
            return "No devices registered"
        
        lines = []
        for name, info in self.devices.items():
            lines.append(
                f"- {name}: {info.device_type} "
                f"(state: {info.current_state}, "
                f"actions: {', '.join(info.available_actions)})"
            )
        return "\n".join(lines)
    
    def build_prompt(self, user_input: str) -> str:
        """
        Build complete prompt for LLM.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            Complete prompt string
        """
        device_list = self.build_device_list()
        system_prompt = self.SYSTEM_PROMPT.format(device_list=device_list)
        
        return f"{system_prompt}\n\nUser Request: {user_input}\n\nJSON Response:"
    
    def clear_devices(self) -> None:
        """Clear all registered devices."""
        self.devices.clear()