"""
Example: AI-powered smart home control with natural language.
"""

import asyncio
import logging
import os
from esp32x import LightController, Light
from smart_home.assistant import SmartHomeAssistant


async def main():
    """
    Demonstrate AI-powered natural language control of ESP32 lights.
    """
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get Gemini API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: Set GEMINI_API_KEY environment variable")
        return
    
    print("=" * 70)
    print("AI Smart Home - Natural Language Device Control")
    print("=" * 70)
    print()
    
    # Connect to ESP32
    print("1. Connecting to ESP32...")
    controller = LightController(device_name="ESP32_Light")
    
    try:
        await controller.connect()
        print("   ✓ Connected to ESP32\n")
        
        # Create devices
        print("2. Initializing devices...")
        bedroom_light = Light(controller)
        kitchen_light = Light(controller)
        
        await bedroom_light.initialize()
        await kitchen_light.initialize()
        print("   ✓ Devices initialized\n")
        
        # Create AI assistant
        print("3. Initializing AI assistant...")
        assistant = SmartHomeAssistant(gemini_api_key=gemini_api_key)
        
        # Register devices
        assistant.register_device("bedroom_light", bedroom_light)
        assistant.register_device("kitchen_light", kitchen_light)
        print("   ✓ AI assistant ready\n")
        
        print("=" * 70)
        print("Testing Natural Language Commands")
        print("=" * 70)
        print()
        
        # Test commands
        test_commands = [
            "Turn on the bedroom light",
            "Please turn off the kitchen light and turn on the bedroom light",
            "What's the status of all lights?",
            "Turn off all lights",
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"\nTest {i}: '{command}'")
            print("-" * 70)
            
            result = await assistant.process(command)
            
            print(f"  AI Response: {result['message']}")
            print(f"  Actions executed: {result['actions_executed']}")
            
            if result['results']:
                print("  Details:")
                for r in result['results']:
                    if r['success']:
                        print(f"    ✓ {r['message']}")
                    else:
                        print(f"    ✗ {r['error']}")
            
            # Small delay between commands
            await asyncio.sleep(1)
        
        print()
        print("=" * 70)
        print("Interactive Mode (type 'quit' to exit)")
        print("=" * 70)
        print()
        
        # Interactive mode
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Exiting...")
                    break
                
                if not user_input:
                    continue
                
                result = await assistant.process(user_input)
                print(f"\nAssistant: {result['message']}")
                
                if result['results']:
                    for r in result['results']:
                        if r['success']:
                            print(f"  ✓ {r['message']}")
                        else:
                            print(f"  ✗ {r['error']}")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
        
    finally:
        print("\nDisconnecting from ESP32...")
        await controller.disconnect()
        print("✓ Disconnected\n")


if __name__ == "__main__":
    asyncio.run(main())