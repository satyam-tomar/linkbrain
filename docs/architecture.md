# LinkBrain Architecture

## Overview

LinkBrain uses a layered architecture that separates hardware control from AI logic, enabling flexible and maintainable code.

## Layer Architecture

```
┌─────────────────────────────────────────┐
│           User Application              │
│         (Your Code)                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       linkbrain_core (AI Layer)         │
│  ┌─────────────────────────────────┐   │
│  │  LLM Providers                  │   │
│  │  (Claude, Gemini)               │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  Prompt Builder                 │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  Action Parser                  │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  Tool Registry                  │   │
│  │  (AI-executable actions)        │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│       linkbrain (Hardware Layer)        │
│  ┌─────────────────────────────────┐   │
│  │  Device Abstractions            │   │
│  │  (Light, Fan, Door)             │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  ESP32 Controller               │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  Connectivity Layer             │   │
│  │  (Bluetooth, WiFi)              │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
         ┌──────▼──────┐
         │   ESP32     │
         │  Hardware   │
         └─────────────┘
```

## Core Components

### 1. linkbrain Package (Hardware Layer)

#### core/
- **controller.py**: Main entry point for ESP32 communication
- **command.py**: Command protocol abstraction
- **exceptions.py**: Hardware-specific exceptions

#### connectivity/
- **base.py**: Abstract connectivity interface
- **bluetooth.py**: BLE implementation using Bleak
- **wifi.py**: TCP/IP implementation

#### devices/
- **base.py**: Abstract device class
- **light.py**, **fan.py**, **door.py**: Device implementations

### 2. linkbrain_core Package (AI Layer)

#### llm/
- **base.py**: Abstract LLM provider
- **anthropic.py**: Claude integration
- **gemini.py**: Gemini integration

#### parsers/
- **action_parser.py**: Parse LLM JSON to executable actions

#### prompts/
- **template.py**: Build structured prompts with device context

#### tools/
- **base.py**: Abstract tool interface
- **registry.py**: Manage and execute tools
- **light.py**, **fan.py**, **door.py**: Device wrappers for AI

## Data Flow

### Basic Control Flow

```
User Code
    ↓
Device (e.g., Light)
    ↓
ESP32Controller
    ↓
Connectivity (Bluetooth/WiFi)
    ↓
ESP32 Hardware
```

### AI Control Flow

```
User Input (Natural Language)
    ↓
PromptBuilder (Add device context)
    ↓
LLM Provider (Generate structured response)
    ↓
ActionParser (Parse JSON to actions)
    ↓
ToolRegistry (Execute actions)
    ↓
Tool (e.g., LightTool)
    ↓
Device (e.g., Light)
    ↓
ESP32Controller
    ↓
ESP32 Hardware
```

## Design Principles

### 1. Separation of Concerns

- **linkbrain**: Knows nothing about AI/LLMs
- **linkbrain_core**: Knows nothing about low-level hardware details
- Each layer has clear responsibilities

### 2. Dependency Inversion

- Abstractions don't depend on concrete implementations
- Use of ABC for interfaces
- Easy to add new connectivity methods or LLM providers

### 3. Single Responsibility

- Each class has one clear purpose
- ESP32Controller: Manage ESP32 connection
- Device: Control physical hardware
- Tool: Wrap device for AI execution

### 4. Open/Closed Principle

- Easy to add new devices without modifying existing code
- Easy to add new LLM providers
- Extension through inheritance

## Exception Hierarchy

### linkbrain Exceptions

```
LinkBrainError
├── ConnectionError
├── CommandError
├── DeviceError
├── TimeoutError
├── InvalidPinError
└── UnsupportedModeError
```

### linkbrain_core Exceptions

```
LLMError
├── LLMConnectionError
├── LLMGenerationError
├── LLMParsingError
├── PromptBuildError
└── ActionValidationError
```

## Extension Points

### Adding a New Device

1. Create device class in `linkbrain/devices/`
2. Inherit from `BaseDevice`
3. Implement `on()`, `off()`, `status()`
4. Create tool wrapper in `linkbrain_core/tools/`
5. Register in tool registry

### Adding a New LLM Provider

1. Create provider in `linkbrain_core/llm/`
2. Inherit from `BaseLLMProvider`
3. Implement `generate()` and `generate_structured()`
4. Add to `__init__.py`

### Adding a New Connectivity Method

1. Create module in `linkbrain/connectivity/`
2. Inherit from `BaseConnectivity`
3. Implement required methods
4. Update `ESP32Controller._create_connectivity()`

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies
- Focus on business logic

### Integration Tests
- Test component interactions
- Use real (or simulated) hardware
- Test complete workflows

### End-to-End Tests
- Test from user input to hardware execution
- Validate AI control flow
- Test error handling

## Performance Considerations

### Connection Management
- Reuse connections when possible
- Handle reconnection automatically
- Implement connection pooling for multiple devices

### LLM Optimization
- Cache common prompts
- Batch multiple commands
- Use streaming for long responses

### Error Recovery
- Automatic retry logic
- Graceful degradation
- Clear error messages

## Security

### API Keys
- Never hardcode API keys
- Use environment variables
- Support secrets management

### Network Security
- Use TLS for WiFi connections
- Validate device certificates
- Implement authentication

### Input Validation
- Validate all user inputs
- Sanitize LLM responses
- Check command parameters

## Future Enhancements

- WebSocket support for real-time updates
- Device discovery and auto-configuration
- Event-driven architecture
- Caching layer for device states
- Metrics and monitoring
- Rate limiting for API calls