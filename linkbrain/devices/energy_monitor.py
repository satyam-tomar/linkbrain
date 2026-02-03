"""
Energy monitor device implementation.
"""

from typing import Dict, Any, Optional
from linkbrain.devices.base import BaseDevice
from linkbrain.core.controller import ESP32Controller
from linkbrain.core.command import Command
from linkbrain.core.exceptions import DeviceError
from linkbrain.utils.logger import get_logger

logger = get_logger(__name__)


class EnergyMonitor(BaseDevice):
    """
    Energy monitor device controlled by ESP32.
    
    Monitors electrical consumption via current/voltage sensors
    connected to ESP32 ADC pins.
    
    Note: This device reads analog values, so it uses ADC-capable pins.
    
    Example:
        >>> monitor = EnergyMonitor(controller, pin=34, name="Main Power Monitor")
        >>> readings = monitor.get_readings()
        >>> print(f"Power: {readings['power_watts']}W")
    """
    
    # ADC-capable pins on ESP32
    ADC_PINS = [32, 33, 34, 35, 36, 39]
    
    def __init__(
        self,
        controller: ESP32Controller,
        pin: int,
        name: Optional[str] = None,
        voltage: float = 220.0,
        calibration_factor: float = 1.0
    ):
        """
        Initialize energy monitor.
        
        Args:
            controller: ESP32Controller instance
            pin: GPIO pin number (must be ADC-capable)
            name: Optional monitor name
            voltage: Line voltage (default 220V)
            calibration_factor: Sensor calibration factor
        
        Raises:
            InvalidPinError: If pin is not ADC-capable
        """
        if pin not in self.ADC_PINS:
            from linkbrain.core.exceptions import InvalidPinError
            raise InvalidPinError(
                f"Pin {pin} is not ADC-capable. Use one of: {self.ADC_PINS}"
            )
        
        super().__init__(controller, pin, name)
        self.voltage = voltage
        self.calibration_factor = calibration_factor
        self._readings = {
            "current_amps": 0.0,
            "power_watts": 0.0,
            "energy_kwh": 0.0
        }
    
    def _initialize_pin(self) -> None:
        """Initialize the GPIO pin as input (ADC mode)."""
        try:
            command = Command.gpio_mode(self.pin, "input")
            response = self.controller.send_command(command)
            if not response.success:
                logger.warning(f"Failed to initialize ADC pin {self.pin}: {response.error}")
        except Exception as e:
            logger.warning(f"Could not initialize ADC pin {self.pin}: {e}")
    
    def get_readings(self) -> Dict[str, float]:
        """
        Get current energy readings.
        
        Returns:
            Dictionary with current, power, and energy readings
        
        Raises:
            DeviceError: If reading fails
        """
        try:
            # Read ADC value
            raw_value = self._get_pin()
            
            # Convert to current (simplified - real implementation would use proper scaling)
            # ADC range: 0-4095 for 0-3.3V
            voltage_reading = (raw_value / 4095.0) * 3.3
            current_amps = voltage_reading * self.calibration_factor
            power_watts = current_amps * self.voltage
            
            self._readings = {
                "current_amps": round(current_amps, 3),
                "power_watts": round(power_watts, 2),
                "voltage": self.voltage,
                "raw_adc": raw_value
            }
            
            logger.debug(f"{self.name} readings: {self._readings}")
            return self._readings
            
        except Exception as e:
            raise DeviceError(f"Failed to read energy data: {str(e)}")
    
    def reset_energy_counter(self) -> None:
        """Reset the accumulated energy counter."""
        self._readings["energy_kwh"] = 0.0
        logger.info(f"{self.name} energy counter reset")
    
    def status(self) -> Dict[str, Any]:
        """
        Get monitor status.
        
        Returns:
            Dictionary with monitor status and latest readings
        """
        try:
            self.get_readings()
        except Exception as e:
            logger.warning(f"Could not get readings: {e}")
        
        return {
            "name": self.name,
            "pin": self.pin,
            "type": "energy_monitor",
            "readings": self._readings,
            "voltage": self.voltage,
            "calibration_factor": self.calibration_factor
        }