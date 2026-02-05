# Migration Guide: Old Structure → New Structure

## Overview

This guide helps you migrate from the old LinkBrain structure to the new production-ready structure.

## Key Changes

### 1. Package Reorganization

**Old Structure:**
```
LinkBrain/
├── core/
├── connectivity/
├── devices/
└── LinkBrain_Core/  # Mixed in the same level
    ├── prompts/
    ├── parsers/
    ├── llm/
    └── tools/
```

**New Structure:**
```
linkbrain_project/
├── linkbrain/          # Hardware layer (clean separation)
│   ├── core/
│   ├── connectivity/
│   ├── devices/
│   └── utils/
└── linkbrain_core/     # AI layer (clean separation)
    ├── llm/
    ├── parsers/
    ├── prompts/
    ├── tools/
    └── exceptions.py
```

### 2. Import Path Changes

**Old Imports:**
```python
from linkbrain.core.controller import ESP32Controller
from linkbrain.devices.light import Light
from linkbrain_core.llm.anthropic import AnthropicProvider
```

**New Imports:**
```python
# Same! But now properly organized
from linkbrain import ESP32Controller, Light
from linkbrain_core.llm import AnthropicProvider
```

### 3. Exception Separation

**Old:**
- All exceptions in one file
- Mixed hardware and AI exceptions

**New:**
- `linkbrain/core/exceptions.py`: Hardware exceptions
- `linkbrain_core/exceptions.py`: AI/LLM exceptions

**Migration:**
```python
# Old
from linkbrain.core.exceptions import ConnectionError, LLMError

# New
from linkbrain.core.exceptions import ConnectionError
from linkbrain_core.exceptions import LLMError
```

### 4. Tool Structure Changes

**Old:**
```python
from linkbrain_tools.light_tool import LightTool
from linkbrain_tools.registry import ToolRegistry
```

**New:**
```python
from linkbrain_core.tools.light import LightTool
from linkbrain_core.tools.registry import ToolRegistry
```

## Step-by-Step Migration

### Step 1: Update Imports

Replace old import paths:

```python
# Before
from linkbrain_core.llm.base import BaseLLMProvider
from linkbrain_core.llm.exceptions import LLMError
from linkbrain_tools.base import BaseToolDevice

# After
from linkbrain_core.llm.base import BaseLLMProvider
from linkbrain_core.exceptions import LLMError
from linkbrain_core.tools.base import BaseToolDevice
```

### Step 2: Update Exception Handling

Separate hardware and AI exceptions:

```python
# Before
try:
    controller.connect()
    llm.generate(prompt)
except LinkBrainError as e:  # Caught everything
    handle_error(e)

# After
try:
    controller.connect()
except ConnectionError as e:  # Hardware specific
    handle_connection_error(e)

try:
    llm.generate(prompt)
except LLMError as e:  # AI specific
    handle_llm_error(e)
```

### Step 3: Update Tool Registration

```python
# Before
from linkbrain_tools.light_tool import LightTool
from linkbrain_tools.registry import ToolRegistry

# After
from linkbrain_core.tools.light import LightTool
from linkbrain_core.tools.registry import ToolRegistry
```

### Step 4: Use New __init__ Exports

Take advantage of cleaner imports:

```python
# Before
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.devices.light import Light
from linkbrain.devices.fan import Fan

# After (cleaner)
from linkbrain import ESP32Controller, Command, Light, Fan
```

### Step 5: Update Configuration

If you had custom configuration files:

```python
# Before
from linkbrain.config import BLUETOOTH_TIMEOUT

# After
from linkbrain.core.controller import ESP32Controller

# Configuration now passed to controller
controller = ESP32Controller(timeout=10.0)
```

## Code Examples

### Basic Device Control

**Before:**
```python
from linkbrain.core.controller import ESP32Controller
from linkbrain.devices.light import Light

controller = ESP32Controller(mode="bluetooth")
controller.connect()
light = Light("living_room", controller, pin=12)
light.on()
```

**After (same, but imports cleaner):**
```python
from linkbrain import ESP32Controller, Light

controller = ESP32Controller(mode="bluetooth")
controller.connect()
light = Light("living_room", controller, pin=12)
light.on()
```

### AI Control

**Before:**
```python
from linkbrain_core.llm.anthropic import AnthropicProvider
from linkbrain_core.parsers.action_parser import ActionParser
from linkbrain_tools.registry import ToolRegistry
from linkbrain_tools.light_tool import LightTool

# Setup code...
```

**After:**
```python
from linkbrain_core.llm.anthropic import AnthropicProvider
from linkbrain_core.parsers.action_parser import ActionParser
from linkbrain_core.tools import ToolRegistry
from linkbrain_core.tools.light import LightTool

# Same setup code...
```

## Benefits of New Structure

### 1. Clear Separation
- Hardware code (`linkbrain`) doesn't know about AI
- AI code (`linkbrain_core`) doesn't know about low-level hardware
- Easier to maintain and test

### 2. Better Organization
- All `__init__.py` files properly configured
- Consistent import patterns
- Clear module responsibilities

### 3. Production-Ready
- Comprehensive logging
- Proper exception hierarchy
- Type hints throughout
- Complete documentation

### 4. Extensibility
- Easy to add new devices
- Easy to add new LLM providers
- Easy to add new connectivity methods

## Common Issues

### Issue 1: Import Errors

**Problem:**
```python
ImportError: No module named 'linkbrain_tools'
```

**Solution:**
```python
# Change to:
from linkbrain_core.tools import ...
```

### Issue 2: Exception Not Found

**Problem:**
```python
ImportError: cannot import name 'LLMError' from 'linkbrain.core.exceptions'
```

**Solution:**
```python
# LLM exceptions are now in linkbrain_core
from linkbrain_core.exceptions import LLMError
```

### Issue 3: Missing __init__.py

**Problem:**
```python
ModuleNotFoundError: No module named 'linkbrain.devices'
```

**Solution:**
- Ensure all `__init__.py` files are present
- Reinstall package: `pip install -e .`

## Testing Your Migration

Run these checks to ensure migration is complete:

```bash
# 1. Check imports work
python -c "from linkbrain import ESP32Controller, Light, Fan"
python -c "from linkbrain_core import ToolRegistry"

# 2. Run tests
pytest tests/

# 3. Try example code
python examples/basic_control.py
```

## Rollback Plan

If you need to rollback:

1. Keep old code in a separate branch
2. Document any custom modifications
3. Test thoroughly before committing to new structure

## Getting Help

- Review documentation in `docs/`
- Check examples in `examples/`
- Open an issue on GitHub
- Join discussions forum

## Timeline

Recommended migration timeline:

1. **Week 1**: Review new structure, update development environment
2. **Week 2**: Migrate imports and test basic functionality
3. **Week 3**: Migrate exception handling and tools
4. **Week 4**: Full testing and documentation update

## Checklist

- [ ] Updated all import statements
- [ ] Separated hardware and AI exceptions
- [ ] Updated tool imports
- [ ] Updated configuration handling
- [ ] Ran all tests successfully
- [ ] Updated documentation
- [ ] Tested in production-like environment
- [ ] Team trained on new structure