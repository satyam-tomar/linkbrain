"""
Basic LinkBrain Usage Example.

This example demonstrates basic device control without AI.
"""

from linkbrain import ESP32Controller, Light, Fan

def main():
    # Initialize controller (Bluetooth mode)
    controller = ESP32Controller(
        mode="bluetooth",
        device_address="AA:BB:CC:DD:EE:FF"  # Replace with your ESP32 MAC
    )
    
    # Connect to ESP32
    print("Connecting to ESP32...")
    controller.connect()
    print("Connected!")
    
    # Create devices
    living_room_light = Light("Living Room", controller, pin=12)
    bedroom_fan = Fan("Bedroom Fan", controller, pin=13)
    
    # Control devices
    print("\nTurning on living room light...")
    living_room_light.on()
    
    print("Turning on bedroom fan...")
    bedroom_fan.on()
    
    # Check status
    print("\nDevice Status:")
    print(f"Light: {living_room_light.status()}")
    print(f"Fan: {bedroom_fan.status()}")
    
    # Turn off devices
    print("\nTurning off devices...")
    living_room_light.off()
    bedroom_fan.off()
    
    # Disconnect
    print("\nDisconnecting...")
    controller.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()