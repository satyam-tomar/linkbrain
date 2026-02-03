"""
Example usage of the ESP32X SDK.

This demonstrates how applications should use the library.
"""

import logging
from linkbrain import ESP32Controller
from linkbrain.devices import Fan, Light, Door, Window, EnergyMonitor
from linkbrain.core.exceptions import LinkBrainError, ConnectionError


def example_basic_usage():
    """Basic usage example with Bluetooth."""
    print("\n=== Example 1: Basic Usage ===\n")
    
    # Initialize controller
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="AA:BB:CC:DD:EE:FF"
    )
    
    try:
        # Connect
        controller.connect()
        print("✓ Connected to ESP32")
        
        # Create devices
        fan = Fan(controller, pin=12, name="Living Room Fan")
        light = Light(controller, pin=14, name="Bedroom Light")
        
        # Control devices
        print("\nControlling devices...")
        fan.on()
        print(f"✓ Fan turned on: {fan.status()}")
        
        light.off()
        print(f"✓ Light turned off: {light.status()}")
        
        # Toggle
        fan.toggle()
        print(f"✓ Fan toggled: {fan.status()}")
        
    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
    except LinkBrainError as e:
        print(f"✗ Error: {e}")
    finally:
        controller.disconnect()
        print("\n✓ Disconnected")


def example_wifi_usage():
    """Example using Wi-Fi connectivity."""
    print("\n=== Example 2: Wi-Fi Connectivity ===\n")
    
    controller = ESP32Controller(
        mode="wifi",
        device_address="192.168.1.100",
        port=8080
    )
    
    try:
        controller.connect()
        print("✓ Connected via Wi-Fi")
        
        door = Door(controller, pin=16, name="Front Door")
        window = Window(controller, pin=18, name="Living Room Window")
        
        print("\nControlling door and window...")
        door.unlock()
        print(f"✓ Door unlocked: {door.status()}")
        
        window.open()
        print(f"✓ Window opened: {window.status()}")
        
        # Lock door for security
        door.lock()
        print(f"✓ Door locked: {door.status()}")
        
    except LinkBrainError as e:
        print(f"✗ Error: {e}")
    finally:
        controller.disconnect()
        print("\n✓ Disconnected")


def example_context_manager():
    """Example using context manager for automatic cleanup."""
    print("\n=== Example 3: Context Manager ===\n")
    
    with ESP32Controller(mode="bluetooth", device_address="AA:BB:CC:DD:EE:FF") as controller:
        light = Light(controller, pin=14, name="Smart Light")
        
        print("Controlling light with context manager...")
        light.on()
        print(f"✓ Light on: {light.status()}")
        
        light.off()
        print(f"✓ Light off: {light.status()}")
    
    print("✓ Automatically disconnected")


def example_energy_monitoring():
    """Example using energy monitor."""
    print("\n=== Example 4: Energy Monitoring ===\n")
    
    controller = ESP32Controller(
        mode="wifi",
        device_address="192.168.1.100"
    )
    
    try:
        controller.connect()
        
        # Energy monitor on ADC-capable pin
        monitor = EnergyMonitor(
            controller,
            pin=34,
            name="Main Power Monitor",
            voltage=220.0
        )
        
        print("Reading energy consumption...")
        readings = monitor.get_readings()
        
        print(f"✓ Current: {readings['current_amps']} A")
        print(f"✓ Power: {readings['power_watts']} W")
        print(f"✓ Voltage: {readings['voltage']} V")
        
        print(f"\nMonitor status: {monitor.status()}")
        
    except LinkBrainError as e:
        print(f"✗ Error: {e}")
    finally:
        controller.disconnect()


def example_multi_device_control():
    """Example controlling multiple devices."""
    print("\n=== Example 5: Multi-Device Control ===\n")
    
    with ESP32Controller(mode="bluetooth", device_address="AA:BB:CC:DD:EE:FF") as controller:
        # Create multiple devices
        devices = {
            "fan": Fan(controller, pin=12, name="Living Room Fan"),
            "light1": Light(controller, pin=14, name="Bedroom Light"),
            "light2": Light(controller, pin=15, name="Kitchen Light"),
            "door": Door(controller, pin=16, name="Front Door"),
        }
        
        print("Turning on all lights and fan...")
        devices["fan"].on()
        devices["light1"].on()
        devices["light2"].on()
        
        print("\nDevice statuses:")
        for name, device in devices.items():
            print(f"  {name}: {device.status()}")
        
        print("\nTurning everything off...")
        devices["fan"].off()
        devices["light1"].off()
        devices["light2"].off()
        devices["door"].lock()
        
        print("\nFinal statuses:")
        for name, device in devices.items():
            print(f"  {name}: {device.status()}")


def example_error_handling():
    """Example demonstrating error handling."""
    print("\n=== Example 6: Error Handling ===\n")
    
    from linkbrain.core.exceptions import InvalidPinError, DeviceError
    
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="AA:BB:CC:DD:EE:FF"
    )
    
    try:
        controller.connect()
        
        # Try to create device with invalid pin
        try:
            invalid_fan = Fan(controller, pin=999)
        except InvalidPinError as e:
            print(f"✓ Caught invalid pin error: {e}")
        
        # Create valid device
        light = Light(controller, pin=14)
        
        # Try operations
        try:
            light.on()
            print("✓ Light operation successful")
        except DeviceError as e:
            print(f"✗ Device error: {e}")
        
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
    except LinkBrainError as e:
        print(f"✗ General ESP32X error: {e}")
    finally:
        controller.disconnect()


def main():
    """Run all examples."""
    # Enable logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("ESP32X SDK - Usage Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_wifi_usage()
    example_context_manager()
    example_energy_monitoring()
    example_multi_device_control()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()