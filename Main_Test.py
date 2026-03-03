import asyncio
import nest_asyncio
nest_asyncio.apply()

from linkbrain import ESP32Controller, Light
from linkbrain_core.llm.gemini import GeminiProvider
from linkbrain_core.prompts.template import PromptBuilder, DeviceContext
from linkbrain_core.parsers.action_parser import ActionParser
from linkbrain_core.tools import ToolRegistry
from linkbrain_core.tools.light import LightTool


async def main():
    # ----------------------------
    # Controller setup
    # ----------------------------
    print("Connecting to ESP32...")
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="3A51DF0E-1520-9120-DA2D-C48E2F714E30"
    )
    
    try:
        controller.connect()
        print("✓ Connected successfully!\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    living_room_light = Light("living_room", controller, pin=4)
    kitchen_light = Light("kitchen", controller, pin=5)  

    # ----------------------------
    # Execution Registry
    # ----------------------------
    registry = ToolRegistry()
    registry.register_device("living_room", LightTool("living_room", living_room_light))
    registry.register_device("kitchen", LightTool("kitchen", kitchen_light))

    # ----------------------------
    # Prompt Context (AI Knowledge)
    # ----------------------------
    prompt_builder = PromptBuilder()
    
    prompt_builder.register_device(
        DeviceContext(
            name="living_room",
            device_type="light",
            current_state="off",
            available_actions={"on", "off", "status"}
        )
    )
    
    prompt_builder.register_device(
        DeviceContext(
            name="kitchen",
            device_type="light",
            current_state="off",
            available_actions={"on", "off", "status"}
        )
    )

    # ----------------------------
    # LLM + Parser
    # ----------------------------
    llm = GeminiProvider(api_key="AIzaSyAuMYcyCIr9BRFgprcpM8kMqZC_OTEse1g")
    parser = ActionParser()

    # ----------------------------
    # Welcome Message
    # ----------------------------
    print("=" * 50)
    print("LinkBrain Interactive Control - FIXED VERSION")
    print("=" * 50)
    print("\nDevices Ready:")
    print("  • Living Room Light (Pin 4)")
    print("  • Kitchen Light (Pin 5)")
    print("\nNote: Pin 2 is reserved for ESP32 heartbeat LED")
    print("\nTry commands like:")
    print("  • 'Turn on the living room light'")
    print("  • 'Turn everything on'")
    print("  • 'Light up the kitchen'")
    print("  • 'Turn off all lights'")
    print("\nType 'exit' to quit\n")

    # ----------------------------
    # Input Loop
    # ----------------------------
    while True:
        try:
            user_input = input(">> ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nShutting down...")
                break

            if not user_input:
                continue

            # Special commands
            if user_input.lower() == "status":
                print("\nDevice Status:")
                print(f"  Living Room: {living_room_light.status()}")
                print(f"  Kitchen: {kitchen_light.status()}")
                continue

            # Process with AI
            print(f"\n🤖 Processing: '{user_input}'")
            
            try:
                # Build prompt with device context
                prompt = prompt_builder.build_prompt(user_input)
                
                # Get AI response
                raw_response = await llm.generate(prompt)
                
                # Parse response
                parsed = parser.parse(raw_response)

                if not parsed.actions:
                    print(f"⚠ {parsed.message}")
                    continue

                # Execute actions
                print(f"⚙ Executing {len(parsed.actions)} action(s)...")
                results = await registry.execute_actions(parsed.actions)
                
                # Show results
                success_count = sum(1 for r in results if r.get("success", False))
                print(f"✓ Completed: {success_count}/{len(results)} successful")
                print(f"   {parsed.message}")
                
                # Show any errors
                for result in results:
                    if not result.get("success", False):
                        print(f"   ✗ Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"✗ Error processing command: {e}")
                print(f"   Try: 'turn on living room' or 'status'")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"✗ Unexpected error: {e}")

    # ----------------------------
    # Cleanup
    # ----------------------------
    print("\nCleaning up...")
    try:
        controller.disconnect()
        print("✓ Disconnected successfully")
    except Exception as e:
        print(f"⚠ Disconnect warning: {e}")
    
    print("\nGoodbye! 👋")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("Make sure ESP32 is powered on and Bluetooth is enabled!")