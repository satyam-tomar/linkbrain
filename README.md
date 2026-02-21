<div align="center">
  <img src="assets/LinkBrain.png" />
</div>

<div align="center">
  <h3>Giving language models a way to act in the real world</h3>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/Version-0.1.0-green" />
  <img src="https://img.shields.io/badge/License-MIT-orange" />
</div>

---

## Overview
**AI agents have officially found their hands.**

Large Language Models are excellent at reasoning, planning, and decision-making inside digital systems. They can book flights, manage workflows, and coordinate complex tasks. But the moment you ask them to interact with the physical world—turn on a light, control a fan, lock a door—they hit a hard boundary.

LinkBrain exists to remove that boundary.

**LinkBrain** is an open-source AI control framework that connects LLMs to real-world hardware (such as ESP32) through a deterministic, contract-driven execution layer. It allows natural language intent to be translated into validated, explicit hardware actions—without giving AI unrestricted or unsafe access to devices.

This is not a chatbot for IoT. It is a control plane for AI-driven physical systems.

---

## What problem does LinkBrain solve?

Most AI–hardware integrations today rely on ad-hoc glue code, fragile parsing, or hundreds of lines of low-level protocol logic. This makes systems difficult to reason about, unsafe to scale, and hardf to audit.

LinkBrain introduces a strict separation of concerns:

- AI systems reason and decide
- LinkBrain validates, constrains, and executes
- Hardware never receives raw AI output

Physical devices are exposed as structured, typed “tools” that an LLM can invoke—but only within predefined contracts.

---

## Key capabilities
LinkBrain provides a production-oriented foundation for AI-to-hardware interaction.

It supports Bluetooth (BLE) and Wi-Fi connectivity, modular ESP32 device abstractions, and structured action execution with logging and validation. The framework enforces clear boundaries between AI reasoning and physical execution, making systems predictable, testable, and auditable.

The SDK is designed for engineers building AI agents, embedded automation pipelines, robotics experiments, or safety-conscious AI–hardware systems.

---

##  Quick Start

### Deterministic device control

```python
from linkbrain import ESP32Controller, Light

# Initialize controller
controller = ESP32Controller(
    mode="bluetooth",
    device_address="AA:BB:CC:DD:EE:FF"
)

# Connect and control
controller.connect()
light = Light("Living Room", controller, pin=12)
light.on()
light.off()
controller.disconnect()
```

### LLM-driven control

```python
import asyncio
from linkbrain import ESP32Controller, Light
from linkbrain_core.llm.anthropic import AnthropicProvider
from linkbrain_core.prompts.template import PromptBuilder
from linkbrain_core.parsers.action_parser import ActionParser
from linkbrain_core.tools import ToolRegistry
from linkbrain_core.tools.light import LightTool

async def main():
    controller = ESP32Controller(mode="bluetooth")
    controller.connect()

    light = Light("living_room", controller, pin=12)

    registry = ToolRegistry()
    registry.register_device("living_room", LightTool("living_room", light))

    llm = AnthropicProvider(api_key="your-key")
    prompt_builder = PromptBuilder()

    user_input = "Turn on the living room light"
    prompt = prompt_builder.build_prompt(user_input)

    response = await llm.generate_structured(prompt)

    parser = ActionParser()
    parsed = parser.parse(response)

    await registry.execute_actions(parsed.actions)

    controller.disconnect()

asyncio.run(main())

```

##  Architecture
LinkBrain is split into two primary layers: a hardware control layer and an AI integration layer. This separation ensures that AI systems never interact with hardware directly.

```
linkbrain/                  # Hardware layer
├── core/                   # ESP32 communication
├── connectivity/           # Bluetooth, WiFi
├── devices/                # Physical devices
└── utils/                  # Utilities

linkbrain_core/             # AI layer
├── llm/                    # LLM providers
├── parsers/                # Response parsing
├── prompts/                # Prompt templates
└── tools/                  # AI-executable tools
```


## Supported Devices
The SDK ships with a small set of reference device abstractions and is designed to be extended.

- **Light**: On/off control
- **Fan**: On/off control
- **Door**: Lock/unlock control
- **Custom**: Easy to extend

##  Supported LLMs
LinkBrain currently integrates with the following providers via structured output interfaces:
- Anthropic Claude (Haiku, Sonnet, Opus)
- Google Gemini (Pro, Pro Vision)


##  Documentation

- [Getting Started Guide](docs/getting_started.md)
- [Architecture Overview](docs/architecture.md)
- [Device Development](docs/device_development.md)


##  Contributing
Contributions are welcome. Please review the contribution guidelines in [Contributing Guide](CONTRIBUTING.md) before submitting pull requests.


##  License

MIT License. See the [LICENSE](LICENSE) file for details.

##  Roadmap

- [ ] More device types (sensors, servos, etc.)
- [ ] WebSocket support for real-time updates
- [ ] Device discovery and auto-configuration
- [ ] Web dashboard for device management
- [ ] MQTT integration
- [ ] Home Assistant integration
