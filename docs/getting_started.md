# Getting Started with LinkBrain

## Installation

### Basic Installation

```bash
pip install linkbrain
```

### With AI Support

```bash
pip install linkbrain[ai]
```

### From Source

```bash
git clone https://github.com/satyam-tomar/linkbrain.git
cd linkbrain
pip install -e ".[dev]"
```

## Hardware Setup

### ESP32 Requirements

1. ESP32 development board
2. Devices connected to GPIO pins:
   - Lights, fans, relays, etc.
3. Bluetooth or WiFi enabled

### Firmware

Upload the LinkBrain firmware to your ESP32:
```bash
# Instructions for firmware upload coming soon
```

## Basic Usage

### 1. Bluetooth Connection

```python
from linkbrain import ESP32Controller, Light

# Initialize controller
controller = ESP32Controller(
    mode="bluetooth",
    device_address="AA:BB:CC:DD:EE:FF"  # Optional, auto-discovers
)

# Connect
controller.connect()

# Create device
light = Light("Living Room", controller, pin=12)

# Control
light.on()
light.off()

# Check status
status = light.status()
print(status)

# Disconnect
controller.disconnect()
```

### 2. WiFi Connection

```python
from linkbrain import ESP32Controller, Fan

controller = ESP32Controller(
    mode="wifi",
    device_address="192.168.1.100",
    port=8080
)

controller.connect()
fan = Fan("Bedroom Fan", controller, pin=13)
fan.on()
controller.disconnect()
```

### 3. Using Context Manager

```python
from linkbrain import ESP32Controller, Light

with ESP32Controller(mode="bluetooth") as controller:
    light = Light("Kitchen", controller, pin=14)
    light.on()
    # Automatically disconnects
```

## AI Integration

### Setup

```python
from linkbrain_core.llm.anthropic import AnthropicProvider
from linkbrain_core.llm.base import LLMConfig

# Configure LLM
config = LLMConfig(
    model="claude-3-haiku-20240307",
    temperature=0.1,
    max_tokens=500
)

# Initialize provider
llm = AnthropicProvider(
    api_key="your-anthropic-api-key",
    config=config
)
```

### Natural Language Control

```python
import asyncio
from linkbrain import ESP32Controller, Light, Fan
from linkbrain_core import ToolRegistry, PromptBuilder
from linkbrain_core.tools import LightTool, FanTool

async def control_devices():
    # Setup hardware
    controller = ESP32Controller(mode="bluetooth")
    controller.connect()
    
    # Create devices
    light = Light("living_room", controller, pin=12)
    fan = Fan("bedroom", controller, pin=13)
    
    # Register tools
    registry = ToolRegistry()
    registry.register_device("living_room", LightTool("living_room", light))
    registry.register_device("bedroom", FanTool("bedroom", fan))
    
    # Build prompt
    builder = PromptBuilder()
    # ... add device contexts
    
    # Execute natural language commands
    user_input = "Turn on all lights and fans"
    # ... process with LLM
    
    controller.disconnect()

asyncio.run(control_devices())
```

## Next Steps

- [API Reference](api_reference.md)
- [Architecture](architecture.md)
- [Device Development](devices/)
- [Examples](../examples/)

## Troubleshooting

### Bluetooth Connection Issues

- Ensure Bluetooth is enabled on your system
- Check ESP32 is in pairing mode
- Verify MAC address is correct

### Device Not Responding

- Check GPIO pin connections
- Verify ESP32 firmware is running
- Check device power supply

### AI Commands Not Working

- Verify API keys are correct
- Check internet connection for LLM APIs
- Review prompt building logic

## Support

- GitHub Issues: [Report bugs](https://github.com/satyam-tomar/linkbrain/issues)
- Discussions: [Ask questions](https://github.com/satyam-tomar/linkbrain/discussions)