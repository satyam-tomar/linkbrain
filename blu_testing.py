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
    # Controller setup (sync)
    # ----------------------------
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="3A51DF0E-1520-9120-DA2D-C48E2F714E30"
    )
    controller.connect()

    # ----------------------------
    # Device + registry
    # ----------------------------
    light = Light("living_room", controller, pin=2)

    registry = ToolRegistry()
    registry.register_device(
        "living_room",
        LightTool("living_room", light)
    )

    # ----------------------------
    # Prompt context
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

    # ----------------------------
    # LLM + parser
    # ----------------------------
    llm = GeminiProvider(api_key="AIzaSyAdZhn8ZvbKe0H_1-7W0Yaf94oKiTh3JnU")
    parser = ActionParser()

    print("\nLinkBrain Interactive Control")
    print("Type commands like: 'turn on the living room light'")
    print("Type 'exit' to quit\n")

    # ----------------------------
    # Input loop
    # ----------------------------
    while True:
        user_input = input(">> ").strip()

        if user_input.lower() == "exit":
            print("Exiting...")
            break

        if not user_input:
            continue

        try:
            prompt = prompt_builder.build_prompt(user_input)
            raw_response = await llm.generate(prompt)

            parsed = parser.parse(raw_response)

            if not parsed.actions:
                print(f"⚠ {parsed.message}")
                continue

            await registry.execute_actions(parsed.actions)
            print(f"✓ {parsed.message}")

        except Exception as e:
            print(f"✗ Error: {e}")

    # ----------------------------
    # Cleanup
    # ----------------------------
    controller.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
