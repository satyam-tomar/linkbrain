# ESP32 Pin Reference for LinkBrain

## 🔴 NEVER USE These Pins

| Pin | Reason | What Happens If Used |
|-----|--------|---------------------|
| 0 | Boot/Flash button | ESP32 may not boot properly |
| 1 | UART TX | Interferes with Serial output |
| 2 | Built-in LED | **Reserved for heartbeat - causes your issue!** |
| 3 | UART RX | Interferes with Serial input |
| 6-11 | Flash memory | **ESP32 will crash/brick!** |

## ✅ SAFE Pins for Your Devices

### Best Pins (No restrictions)
```
📍 Recommended for lights, fans, relays, etc.:
   4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23
```

### Good Pins (Some considerations)
```
📍 Usable, but check if needed for other purposes:
   25, 26, 27, 32, 33
   (These are often used for analog input)
```

### Input-Only Pins
```
📍 Can only read (sensors, buttons):
   34, 35, 36, 39
   (Cannot be used for OUTPUT like lights/relays)
```

## 📋 Example Device Mapping

### For Your Setup:

```python
# Python code
living_room_light = Light("living_room", controller, pin=4)
kitchen_light = Light("kitchen", controller, pin=5)
bedroom_fan = Fan("bedroom_fan", controller, pin=12)
front_door = Door("front_door", controller, pin=13)
garden_light = Light("garden", controller, pin=14)
bathroom_fan = Fan("bathroom_fan", controller, pin=15)
```

### Wiring Diagram:

```
ESP32 DevKit V1
┌────────────────────┐
│                    │
│  GND  ●            │─── GND to all devices
│  3.3V ●            │─── Power (if needed)
│  EN   ●            │
│  VP   ●            │
│  VN   ●            │
│  34   ●            │
│  35   ●            │
│  32   ●            │
│  33   ●            │
│  25   ●            │
│  26   ●            │
│  27   ●            │
│  14   ●────────────┼─── Garden Light
│  12   ●────────────┼─── Bedroom Fan
│  13   ●────────────┼─── Front Door Lock
│  15   ●────────────┼─── Bathroom Fan
│  2    ●  [RESERVED]│─── Heartbeat LED (DON'T USE)
│  0    ●  [RESERVED]│─── Boot Button
│  4    ●────────────┼─── Living Room Light
│  16   ●            │
│  17   ●            │
│  5    ●────────────┼─── Kitchen Light
│  18   ●            │
│  19   ●            │
│  21   ●            │
│  RX   ●  [RESERVED]│─── Serial RX
│  TX   ●  [RESERVED]│─── Serial TX
│  22   ●            │
│  23   ●            │
│  GND  ●            │
│  VIN  ●            │─── External power (optional)
│                    │
└────────────────────┘
```

## 🔧 Testing Each Pin

### Python Script to Test All Safe Pins:

```python
from linkbrain import ESP32Controller
from linkbrain.core.command import Command
import time

controller = ESP32Controller(mode="bluetooth")
controller.connect()

safe_pins = [4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23]

print("Testing safe pins...")
for pin in safe_pins:
    print(f"\nTesting pin {pin}...")
    
    # Turn ON
    response = controller.send_command(Command.gpio_set(pin, 1))
    print(f"  ON: {response.success}")
    time.sleep(0.5)
    
    # Turn OFF
    response = controller.send_command(Command.gpio_set(pin, 0))
    print(f"  OFF: {response.success}")
    time.sleep(0.5)

print("\n✓ Test complete!")
controller.disconnect()
```

## 📱 Quick Reference Chart

### By Use Case:

| Use Case | Recommended Pins | Example |
|----------|-----------------|---------|
| Lights (Relays) | 4, 5, 14, 15, 16, 17 | `Light("living", ctrl, pin=4)` |
| Motors/Fans | 12, 13, 18, 19 | `Fan("ceiling", ctrl, pin=12)` |
| Door Locks | 21, 22, 23 | `Door("front", ctrl, pin=21)` |
| Sensors (Input) | 25, 26, 27, 32, 33 | `pinMode(25, INPUT)` |
| Buttons (Input) | 34, 35, 36, 39 | Read only, no OUTPUT |

## ⚠️ Common Mistakes

### Mistake #1: Using Pin 2
```python
# ❌ WRONG - Pin 2 is heartbeat LED
light = Light("living", controller, pin=2)

# ✅ CORRECT - Use pin 4 or higher
light = Light("living", controller, pin=4)
```

### Mistake #2: Using Flash Pins
```python
# ❌ WRONG - Will crash ESP32
light = Light("living", controller, pin=6)

# ✅ CORRECT - Use safe pins
light = Light("living", controller, pin=12)
```

### Mistake #3: Output on Input-Only Pins
```python
# ❌ WRONG - Pin 34 is input-only
light = Light("living", controller, pin=34)

# ✅ CORRECT - Use output-capable pins
light = Light("living", controller, pin=4)
```

## 🎯 Your Fixed Configuration

### From Your Test File (CORRECTED):

```python
# OLD (BROKEN) - Don't use this!
living_room_light = Light("living_room", controller, pin=2)  # ❌ Conflicts with heartbeat

# NEW (FIXED) - Use this instead!
living_room_light = Light("living_room", controller, pin=4)  # ✅ Safe pin
kitchen_light = Light("kitchen", controller, pin=5)          # ✅ Safe pin
```

## 📊 Pin Capability Matrix

| Pin | Output | Input | PWM | ADC | Touch | I2C | SPI | Notes |
|-----|--------|-------|-----|-----|-------|-----|-----|-------|
| 0 | ⚠️ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | Boot pin |
| 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | TX - Don't use |
| 2 | ⚠️ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RESERVED - LED** |
| 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | RX - Don't use |
| 4 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RECOMMENDED** |
| 5 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | **RECOMMENDED** |
| 12 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RECOMMENDED** |
| 13 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RECOMMENDED** |
| 14 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RECOMMENDED** |
| 15 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | **RECOMMENDED** |

## 🚀 Quick Setup Guide

### 1. Hardware Setup
```
Wire your devices to safe pins:
- Lights/LEDs → Pins 4, 5, 14, 15
- Relays     → Pins 12, 13, 16, 17
- Motors     → Pins 18, 19, 21, 22
```

### 2. Upload Fixed Firmware
```arduino
// Make sure this line is in your firmware:
#define HEARTBEAT_LED LED_BUILTIN  // Reserves pin 2
```

### 3. Python Configuration
```python
# Use safe pins only!
devices = {
    "living_room": 4,
    "kitchen": 5,
    "bedroom": 12,
    "bathroom": 13,
    "garden": 14
}
```

## 💡 Pro Tips

1. **Always check Serial Monitor** - It shows pin conflicts
2. **Start with one device** - Test pin 4 first
3. **Use pin labels** - Mark your wires!
4. **Avoid pin 2** - That's your whole problem!
5. **Test before wiring** - Use the test script above

---

**Quick Answer to Your Issue:**
- ❌ You used **pin 2** for the living room light
- ⚡ Pin 2 is the **heartbeat LED** that blinks every 3 seconds
- 🔄 The heartbeat kept turning **your light off**
- ✅ Solution: Use **pin 4** instead of pin 2!

**Result:** Your light will now stay ON permanently! ✨