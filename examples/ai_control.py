"""
AI-Powered Device Control Example.

This example demonstrates using LLMs to control devices via natural language.
"""

import asyncio
from linkbrain import ESP32Controller, Light, Fan, Door
from linkbrain_core.llm.anthropic import AnthropicProvider
from linkbrain_core.llm.base import LLMConfig
from linkbrain_core.prompts.template import PromptBuilder, DeviceContext
from linkbrain_core.parsers.action_parser import ActionParser
from linkbrain_core.tools import ToolRegistry
from linkbrain_core.tools.light import LightTool
from linkbrain_core.tools.fan import FanTool
from linkbrain_core.tools.door import DoorTool


async def main():
    # Initialize ESP32 controller
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="AA:BB:CC:DD:EE:FF"
    )
    controller.connect()
    
    # Create physical devices
    living_light = Light("living_room_light", controller, pin=12)
    bedroom_fan = Fan("bedroom_fan", controller, pin=13)
    front_door = Door("front_door", controller, pin=14)
    
    # Create AI tools
    tool_registry = ToolRegistry()
    tool_registry.register_device("living_room_light", LightTool("living_room_light", living_light))
    tool_registry.register_device("bedroom_fan", FanTool("bedroom_fan", bedroom_fan))
    tool_registry.register_device("front_door", DoorTool("front_door", front_door))
    
    # Initialize LLM
    llm_config = LLMConfig(model="claude-3-haiku-20240307")
    llm = AnthropicProvider(api_key="your-api-key", config=llm_config)
    
    # Build prompt with device context
    prompt_builder = PromptBuilder()
    for name, tool in tool_registry.devices.items():
        context = DeviceContext(
            name=name,
            device_type=type(tool).__name__,
            current_state="unknown",
            available_actions=tool.supported_actions()
        )
        prompt_builder.register_device(context)
    
    # Natural language command
    user_input = "Turn on the living room light and bedroom fan"
    
    # Generate prompt
    prompt = prompt_builder.build_prompt(user_input)
    
    # Get LLM response
    print(f"User: {user_input}")
    print("\nSending to LLM...")
    response = await llm.generate_structured(prompt)
    
    # Parse actions
    parser = ActionParser()
    import json
    parsed = parser.parse(json.dumps(response))
    
    # Execute actions
    print(f"\nExecuting {len(parsed.actions)} actions...")
    results = await tool_registry.execute_actions(parsed.actions)
    
    # Show results
    for result in results:
        print(f"  - {result}")
    
    print(f"\nAssistant: {parsed.message}")
    
    # Cleanup
    controller.disconnect()


if __name__ == "__main__":
    asyncio.run(main())