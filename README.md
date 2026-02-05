<div align="center">
  <img src="assets/LinkBrain.png" width="420" />
</div>

<div align="center">
  <h3>A developer framework for AI-driven physical systems</h3>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/Version-0.1.0-green" />
  <img src="https://img.shields.io/badge/License-MIT-orange" />
</div>

---
# LinkBrain SDK

A developer framework for safely controlling ESP32-based physical systems using AI-generated intent.

---

## Overview

**LinkBrain** is an AI-enabled control framework that allows developers to connect large language models with ESP32 hardware through a deterministic, contract-driven execution layer. It enables natural language interaction with physical devices while ensuring that all hardware actions are validated, explicit, and auditable.

The SDK is designed for engineers building AI-driven physical agents, embedded automation systems, or experimental AI–hardware integrations where safety, predictability, and system boundaries are critical.

---

## Key capabilities

LinkBrain provides a structured foundation for AI-to-hardware interaction. It supports multiple communication protocols, exposes high-level device abstractions, and cleanly separates AI reasoning from physical execution. The framework is written with production-quality engineering practices, including type safety, logging, and testability.

Core capabilities include Bluetooth (BLE) and Wi-Fi connectivity, modular device definitions, integration with modern LLM providers, and a layered architecture that keeps AI logic isolated from hardware control.

---

## Installation

```bash
pip install linkbrain

# Install with AI integrations
pip install linkbrain[ai]

# Install development dependencies
pip install linkbrain[dev]

```

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
    # Setup
    controller = ESP32Controller(mode="bluetooth")
    controller.connect()
    
    light = Light("living_room", controller, pin=12)
    registry = ToolRegistry()
    registry.register_device("living_room", LightTool("living_room", light))
    
    # Initialize AI
    llm = AnthropicProvider(api_key="your-key")
    prompt_builder = PromptBuilder()
    
    # Natural language control
    user_input = "Turn on the living room light"
    prompt = prompt_builder.build_prompt(user_input)
    response = await llm.generate_structured(prompt)
    
    # Execute
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

##  Documentation

- [Getting Started Guide](docs/getting_started.md)
- [API Reference](docs/api_reference.md)
- [Architecture Overview](docs/architecture.md)
- [Device Development](docs/devices/)

## Supported Devices
The SDK ships with a small set of reference device abstractions and is designed to be extended.

- **Light**: On/off control
- **Fan**: On/off control
- **Door**: Lock/unlock control
- **Custom**: Easy to extend

##  Supported LLMs
LinkBrain currently integrates with the following providers through structured output interfaces:
- Anthropic Claude (Haiku, Sonnet, Opus)
- Google Gemini (Pro, Pro Vision)

##  Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=linkbrain --cov=linkbrain_core

# Specific module
pytest tests/unit/test_devices/
```

##  Development

```bash
# Clone repository
git clone https://github.com/yourusername/linkbrain.git
cd linkbrain

# Install in development mode
pip install -e ".[dev]"

# Run linters
black .
flake8 .
mypy .

# Run tests
pytest
```

##  Project Structure

```
linkbrain_project/
├── linkbrain/              # Main SDK package
│   ├── core/               # Core communication
│   ├── connectivity/       # Protocol implementations
│   ├── devices/            # Device abstractions
│   └── utils/              # Utilities
├── linkbrain_core/         # AI integration layer
│   ├── llm/                # LLM providers
│   ├── parsers/            # Response parsing
│   ├── prompts/            # Prompt templates
│   └── tools/              # AI tools
├── examples/               # Usage examples
├── tests/                  # Test suite
├── docs/                   # Documentation
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
└── README.md               # This file
```

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