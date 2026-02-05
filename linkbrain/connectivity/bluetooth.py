"""
Bluetooth connectivity implementation for ESP32.

Supports both write-only (fire-and-forget) and write+read (request-response)
communication patterns with ESP32 devices via BLE.
"""

import asyncio
from typing import Optional
import logging

try:
    from bleak import BleakScanner, BleakClient
except ImportError:
    raise ImportError(
        "Bleak not installed. Install with: pip install bleak"
    )

from linkbrain.connectivity.base import BaseConnectivity
from linkbrain.core.command import Command, CommandResponse
from linkbrain.core.exceptions import ConnectionError, CommandError, TimeoutError

logger = logging.getLogger(__name__)

__all__ = ['BluetoothConnectivity']

# Nordic UART Service UUIDs
SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
WRITE_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
READ_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class BluetoothConnectivity(BaseConnectivity):
    """
    Bluetooth connectivity implementation for ESP32.
    
    Supports both:
    - Fire-and-forget (write-only) mode
    - Request-response (write + read/notify) mode
    
    The mode is auto-detected based on available characteristics.
    
    Example:
        >>> bt = BluetoothConnectivity(device_address="AA:BB:CC:DD:EE:FF")
        >>> bt.connect()
        >>> response = bt.send_command(Command.gpio_set(12, 1))
        >>> bt.disconnect()
    """

    def __init__(
        self,
        device_address: Optional[str] = None,
        timeout: float = 5.0
    ):
        """
        Initialize Bluetooth connectivity.
        
        Args:
            device_address: MAC address of ESP32 (optional, will auto-discover)
            timeout: Connection timeout in seconds
        """
        super().__init__(device_address or "auto-discover", timeout)

        self._client: Optional[BleakClient] = None
        self._device = None
        self._loop = asyncio.new_event_loop()
        
        # Auto-detected capabilities
        self._has_read_char = False
        self._has_notify_char = False
        self._response_data = None  # For notify responses

        logger.info("Bluetooth connectivity initialized")

    def connect(self) -> None:
        """
        Establish Bluetooth connection to ESP32.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info("Connecting to ESP32 via Bluetooth (BLE)")
            self._run(self._connect_async())
            self._connected = True
            logger.info("Bluetooth connection established")
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect via Bluetooth: {e}")

    def disconnect(self) -> None:
        """Disconnect from ESP32."""
        if not self._connected:
            return

        try:
            self._run(self._disconnect_async())
            logger.info("Bluetooth disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._connected = False
            self._client = None

    def send_command(self, command: Command) -> CommandResponse:
        """
        Send command via Bluetooth.
        
        Automatically handles both fire-and-forget and request-response modes.
        
        Args:
            command: Command to send
        
        Returns:
            Command response
        
        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
            TimeoutError: If command times out
        """
        if not self._connected or not self._client:
            raise ConnectionError("Not connected to ESP32")

        try:
            raw = self._run(self._send_command_async(command))
            return CommandResponse.from_string(raw)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Command timed out after {command.timeout}s")
        except Exception as e:
            raise CommandError(f"Command failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected and self._client is not None

    # Private async methods

    async def _connect_async(self):
        """Async connection logic."""
        if not self._device:
            self._device = await self._discover_device()

        self._client = BleakClient(self._device)
        await asyncio.wait_for(self._client.connect(), timeout=self.timeout)

        if not self._client.is_connected:
            raise ConnectionError("BLE connection failed")
        
        # Auto-detect available characteristics
        await self._detect_characteristics()

    async def _disconnect_async(self):
        """Async disconnection logic."""
        if self._client:
            await self._client.disconnect()

    async def _detect_characteristics(self):
        """
        Detect which characteristics are available on the ESP32.
        This determines whether we use fire-and-forget or request-response.
        """
        try:
            services = self._client.services
            
            for service in services:
                for char in service.characteristics:
                    if char.uuid.lower() == READ_CHAR_UUID.lower():
                        self._has_read_char = "read" in char.properties
                        self._has_notify_char = "notify" in char.properties
                        
                        if self._has_notify_char:
                            # Set up notification handler
                            await self._client.start_notify(
                                READ_CHAR_UUID, 
                                self._notification_handler
                            )
                        
                        logger.info(
                            f"Response channel detected: "
                            f"read={self._has_read_char}, "
                            f"notify={self._has_notify_char}"
                        )
                        return
            
            logger.info("No response channel - using fire-and-forget mode")
            
        except Exception as e:
            logger.warning(f"Error detecting characteristics: {e}")
            logger.info("Defaulting to fire-and-forget mode")

    def _notification_handler(self, sender, data: bytearray):
        """Handle notifications from ESP32."""
        self._response_data = data.decode("utf-8")
        logger.debug(f"Received notification: {self._response_data}")

    async def _send_command_async(self, command: Command) -> str:
        """
        Send command and await response (if available).
        
        Three modes:
        1. Notify mode (preferred): write → wait for notification
        2. Read mode: write → read characteristic
        3. Fire-and-forget: write → return "OK"
        
        Args:
            command: Command to send
        
        Returns:
            Response string from ESP32
        """
        payload = command.to_protocol_string().encode("utf-8")
        logger.debug(f"Sending: {payload}")

        # Always write the command
        await self._client.write_gatt_char(WRITE_CHAR_UUID, payload)
        
        # Handle response based on available characteristics
        if self._has_notify_char:
            # Wait for notification
            self._response_data = None
            timeout = command.timeout
            elapsed = 0
            
            while self._response_data is None and elapsed < timeout:
                await asyncio.sleep(0.1)
                elapsed += 0.1
            
            if self._response_data is None:
                logger.warning("No notification received, assuming success")
                return "OK"
            
            return self._response_data
            
        elif self._has_read_char:
            # Read the response characteristic
            data = await asyncio.wait_for(
                self._client.read_gatt_char(READ_CHAR_UUID),
                timeout=command.timeout
            )
            return data.decode("utf-8")
        
        else:
            # Fire-and-forget mode - no response expected
            logger.debug("Command sent (fire-and-forget)")
            return "OK"

    async def _discover_device(self):
        """
        Discover ESP32 BLE device.
        
        Returns:
            BLE device object
        
        Raises:
            ConnectionError: If device not found
        """
        logger.info("Scanning for ESP32 BLE device")

        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: ad.service_uuids
            and SERVICE_UUID.lower() in [s.lower() for s in ad.service_uuids]
        )

        if not device:
            raise ConnectionError("ESP32 BLE device not found")

        logger.info(f"Found device: {device.name or device.address}")
        return device

    def _run(self, coro):
        """Run async coroutine in the event loop."""
        return self._loop.run_until_complete(coro)