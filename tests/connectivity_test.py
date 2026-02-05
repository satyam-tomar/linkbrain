import asyncio
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

async def trigger_test():
    print("Step 1: Searching for ESP32...")
    
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: SERVICE_UUID.lower() in [s.lower() for s in ad.service_uuids]
    )

    if not device:
        print("Error: Could not find ESP32. If it's connected elsewhere, disconnect it first.")
        return

    print(f"Step 2: Found {device.name or 'Device'}. Connecting...")
    
    try:
        # The 'async with' block handles the connection AND the disconnection automatically
        async with BleakClient(device) as client:
            if client.is_connected:
                print("Step 3: Connected! Sending 'blink'...")
                
                await client.write_gatt_char(CHARACTERISTIC_UUID, b"blink")
                print("Step 4: Command sent successfully.")
                
                # We wait briefly to ensure the ESP32 receives the full packet
                await asyncio.sleep(1.0) 
                
                print("Step 5: Task complete. Closing connection...")
            
            # The moment we exit this 'with' block, the client disconnects.
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Done. The ESP32 is now free for new connections.")

if __name__ == "__main__":
    asyncio.run(trigger_test())