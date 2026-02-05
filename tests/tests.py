"""
AI Smart Home Assistant - Main interface.
"""

import logging
from typing import Dict, Any
from esp32x.devices.light import Light
from smart_home.ai.prompts.template import PromptTemplate, DeviceInfo
from smart_home.ai.providers.gemini import GeminiProvider
from smart_home.ai.parsers.action_parser import ActionParser
from smart_home.ai.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class SmartHomeAssistant:
    """
    AI-powered smart home assistant.
    
    Translates natural language commands into device actions.
    """
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize smart home assistant.
        
        Args:
            gemini_api_key: Google AI API key for Gemini
        """
        self.prompt_template = PromptTemplate()
        self.llm = GeminiProvider(api_key=gemini_api_key)
        self.parser = ActionParser()
        self.tools = ToolRegistry()
        
        logger.info("Smart Home Assistant initialized")
    
    def register_device(self, name: str, device: Light) -> None:
        """
        Register a device for AI control.
        
        Args:
            name: Device name (e.g., "bedroom_light", "kitchen_light")
            device: Light instance
        """
        # Register in tool registry
        self.tools.register_device(name, device)
        
        # Register in prompt template
        device_info = DeviceInfo(
            name=name,
            device_type="Light",
            current_state=device.state,
            available_actions=["on", "off", "status"]
        )
        self.prompt_template.register_device(device_info)
        
        logger.info(f"Device '{name}' registered with assistant")
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process natural language command.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            Result dictionary with actions taken and message
        """
        try:
            logger.info(f"Processing user input: '{user_input}'")
            
            # Build prompt
            prompt = self.prompt_template.build_prompt(user_input)
            logger.debug(f"Prompt built (length: {len(prompt)})")
            
            # Get LLM response
            llm_output = await self.llm.generate(prompt)
            logger.debug(f"LLM output: {llm_output}")
            
            # Parse response
            parsed = self.parser.parse(llm_output)
            logger.info(f"Parsed {len(parsed.actions)} actions")
            
            # Execute actions
            results = await self.tools.execute_actions(parsed.actions)
            
            # Build response
            successful_actions = [r for r in results if r.get("success")]
            failed_actions = [r for r in results if not r.get("success")]
            
            response = {
                "success": len(failed_actions) == 0,
                "message": parsed.message,
                "actions_executed": len(successful_actions),
                "actions_failed": len(failed_actions),
                "results": results,
                "user_input": user_input
            }
            
            logger.info(
                f"Completed: {len(successful_actions)} successful, "
                f"{len(failed_actions)} failed"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "actions_executed": 0,
                "actions_failed": 0,
                "results": [],
                "user_input": user_input,
                "error": str(e)
            }
    
    def get_device_status(self) -> Dict[str, str]:
        """
        Get status of all registered devices.
        
        Returns:
            Dictionary mapping device names to states
        """
        return self.tools.list_devices()