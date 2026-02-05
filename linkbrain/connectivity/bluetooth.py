"""
Bluetooth connectivity implementation for ESP32.
"""

import time
import asyncio
from typing import Optional

from bleak import BleakScanner, BleakClient

from linkbrain.connectivity.base import BaseConnectivity
from linkbrain.core.command import Command, CommandResponse
from linkbrain.core.exceptions import ConnectionError, CommandError, TimeoutError
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
WRITE_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
READ_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class BluetoothConnectivity(BaseConnectivity):
    """
    Bluetooth connectivity implementation for ESP32.
    """

    def __init__(self, device_address: Optional[str] = None, timeout: float = 5.0):
        super().__init__(device_address, timeout)

        self._client: Optional[BleakClient] = None
        self._device = None
        self._loop = asyncio.new_event_loop()

        logger.info("Bluetooth connectivity initialized")

    def connect(self) -> None:
        """
        Establish Bluetooth connection to ESP32.
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
        return self._connected


    async def _connect_async(self):
        if not self._device:
            self._device = await self._discover_device()

        self._client = BleakClient(self._device)
        await asyncio.wait_for(self._client.connect(), timeout=self.timeout)

        if not self._client.is_connected:
            raise ConnectionError("BLE connection failed")

    async def _disconnect_async(self):
        if self._client:
            await self._client.disconnect()

    async def _send_command_async(self, command: Command) -> str:
        payload = command.to_protocol_string().encode("utf-8")

        await self._client.write_gatt_char(WRITE_CHAR_UUID, payload)

        if READ_CHAR_UUID:
            data = await asyncio.wait_for(
                self._client.read_gatt_char(READ_CHAR_UUID),
                timeout=command.timeout
            )
            return data.decode("utf-8")

        return "OK"

    async def _discover_device(self):
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
        return self._loop.run_until_complete(coro)
