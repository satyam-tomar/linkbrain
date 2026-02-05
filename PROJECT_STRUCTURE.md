# LinkBrain Project Structure

## Overview
Production-ready structure for LinkBrain - an AI-powered ESP32 control framework.

```
linkbrain_project/
│
├── linkbrain/                          # Main SDK package
│   ├── __init__.py
│   ├── core/                           # Core ESP32 communication layer
│   │   ├── __init__.py
│   │   ├── controller.py               # Main ESP32 controller
│   │   ├── command.py                  # Command protocol
│   │   └── exceptions.py               # SDK exceptions
│   │
│   ├── connectivity/                   # Connectivity implementations
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract connectivity interface
│   │   ├── bluetooth.py                # BLE implementation
│   │   └── wifi.py                     # WiFi/TCP implementation
│   │
│   ├── devices/                        # Physical device abstractions
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract device class
│   │   ├── light.py                    # Light device
│   │   ├── fan.py                      # Fan device
│   │   ├── door.py                     # Door lock device
│   │   └── ...                         # Other devices
│   │
│   └── utils/                          # Utilities
│       ├── __init__.py
│       └── logger.py                   # Logging utilities
│
├── linkbrain_core/                     # AI/LLM integration layer
│   ├── __init__.py
│   ├── llm/                            # LLM providers
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract LLM provider
│   │   ├── anthropic.py                # Claude provider
│   │   └── gemini.py                   # Gemini provider
│   │
│   ├── parsers/                        # Response parsing
│   │   ├── __init__.py
│   │   └── action_parser.py            # Parse LLM output to actions
│   │
│   ├── prompts/                        # Prompt management
│   │   ├── __init__.py
│   │   └── template.py                 # Prompt templates
│   │
│   ├── tools/                          # AI-executable tools
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract tool device
│   │   ├── registry.py                 # Tool registry
│   │   ├── light.py                    # Light tool wrapper
│   │   ├── fan.py                      # Fan tool wrapper
│   │   └── door.py                     # Door tool wrapper
│   │
│   └── exceptions.py                   # LLM/AI-specific exceptions
│
├── examples/                           # Usage examples
│   ├── basic_control.py
│   ├── ai_control.py
│   └── multi_device.py
│
├── tests/                              # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docs/                               # Documentation
│   ├── getting_started.md
│   ├── api_reference.md
│   └── architecture.md
│
├── setup.py                            # Package setup
├── requirements.txt                    # Dependencies
├── README.md                           # Project README
└── .gitignore                          # Git ignore rules
```

## Key Design Principles

### 1. Separation of Concerns
- **linkbrain/**: Low-level ESP32 communication (no AI)
- **linkbrain_core/**: AI/LLM integration layer (no direct hardware)

### 2. Exception Hierarchy
```
LinkBrainError (base)
├── ConnectionError
├── CommandError
├── DeviceError
├── TimeoutError
└── InvalidPinError

LLMError (base)
├── LLMConnectionError
├── LLMGenerationError
└── LLMParsingError
```

### 3. Dependency Flow
```
linkbrain_core → linkbrain → ESP32 Hardware
     ↓               ↓
   LLM APIs    Physical Devices
```

### 4. Module Responsibilities

#### linkbrain/core/
- ESP32 communication protocol
- Connection management
- Command execution
- Low-level exceptions

#### linkbrain/connectivity/
- Abstract connectivity interface
- Bluetooth (BLE) implementation
- WiFi (TCP) implementation
- Connection lifecycle management

#### linkbrain/devices/
- Physical device abstractions
- Device-specific logic
- State management
- Direct hardware control

#### linkbrain_core/llm/
- LLM provider interfaces
- API client management
- Prompt generation
- Response handling

#### linkbrain_core/parsers/
- LLM response parsing
- Action extraction
- Validation

#### linkbrain_core/prompts/
- Prompt templates
- Context building
- Device state formatting

#### linkbrain_core/tools/
- AI-executable wrappers
- Tool registry
- Action execution
- High-level device control

## Import Patterns

### Good Patterns ✅
```python
# From user code
from linkbrain import ESP32Controller
from linkbrain.devices import Light, Fan
from linkbrain_core import AIController
from linkbrain_core.llm import AnthropicProvider

# Within linkbrain
from linkbrain.core import Command, CommandResponse
from linkbrain.core.exceptions import ConnectionError

# Within linkbrain_core
from linkbrain_core.llm.base import BaseLLMProvider
from linkbrain_core.exceptions import LLMError
```

### Anti-Patterns ❌
```python
# Don't cross boundaries inappropriately
from linkbrain.connectivity.bluetooth import WRITE_CHAR_UUID  # Too specific
from linkbrain_core.tools.light import LightTool  # Use registry instead
```

## __init__.py Strategy

### Top-level Package Exports
Each package exposes its public API through `__init__.py`:

```python
# linkbrain/__init__.py
from linkbrain.core.controller import ESP32Controller
from linkbrain.devices import Light, Fan, Door

__all__ = ['ESP32Controller', 'Light', 'Fan', 'Door']
```

### Sub-package Exports
Sub-packages expose their components:

```python
# linkbrain/devices/__init__.py
from .light import Light
from .fan import Fan
from .door import Door

__all__ = ['Light', 'Fan', 'Door']
```

## Exception Placement

### linkbrain/core/exceptions.py
Hardware and communication exceptions:
- ConnectionError
- CommandError
- DeviceError
- TimeoutError
- InvalidPinError

### linkbrain_core/exceptions.py
AI and LLM exceptions:
- LLMError (base)
- LLMConnectionError
- LLMGenerationError
- LLMParsingError

## Configuration Management

Configuration should be centralized:
```python
# linkbrain/config.py
DEFAULT_BLUETOOTH_TIMEOUT = 5.0
DEFAULT_WIFI_PORT = 8080

# linkbrain_core/config.py
DEFAULT_LLM_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 500
```

## Testing Structure
```
tests/
├── unit/
│   ├── test_command.py
│   ├── test_connectivity/
│   │   ├── test_bluetooth.py
│   │   └── test_wifi.py
│   ├── test_devices/
│   │   ├── test_light.py
│   │   └── test_fan.py
│   └── test_llm/
│       ├── test_anthropic.py
│       └── test_parser.py
├── integration/
│   ├── test_bluetooth_control.py
│   └── test_ai_control.py
└── conftest.py
```

## Documentation Structure
```
docs/
├── getting_started.md      # Quick start guide
├── architecture.md         # System design
├── api_reference.md        # API documentation
├── devices/                # Device-specific docs
│   ├── light.md
│   ├── fan.md
│   └── door.md
└── examples/               # Usage examples
    ├── basic_control.md
    └── ai_integration.md
```