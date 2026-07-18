import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class RuleRuntime:
    """A clean, threshold-based engine for rule-based diagnostic evaluation."""

    def evaluate_temperature(self, temp: float) -> Tuple[str, float, str]:
        """Evaluate temperature rules.
        
        Returns:
            Tuple of (status, severity, reason)
        """
        if temp >= 105.0:
            return "emergency", 95.0, f"Critical engine overheating: {temp}°C"
        elif temp >= 90.0:
            return "critical", 80.0, f"High engine temperature: {temp}°C"
        elif temp >= 75.0:
            return "warning", 50.0, f"Elevated engine temperature: {temp}°C"
        else:
            return "safe", 0.0, f"Engine temperature normal: {temp}°C"

    def evaluate_battery(self, voltage: float) -> Tuple[str, float, str]:
        """Evaluate battery voltage rules.
        
        Returns:
            Tuple of (status, severity, reason)
        """
        if voltage < 10.5 or voltage > 16.0:
            return "emergency", 98.0, f"Severe battery voltage anomaly: {voltage}V"
        elif voltage < 11.5 or voltage > 15.0:
            return "critical", 85.0, f"Critical battery voltage: {voltage}V"
        elif voltage < 12.2 or voltage > 14.5:
            return "warning", 55.0, f"Low battery voltage warning: {voltage}V"
        else:
            return "safe", 0.0, f"Battery voltage normal: {voltage}V"

    def evaluate_smoke(self, gas_level: float, digital: int) -> Tuple[str, float, str]:
        """Evaluate smoke sensor rules.
        
        Returns:
            Tuple of (status, severity, reason)
        """
        if digital == 1 or gas_level >= 800.0:
            return "emergency", 99.0, f"Smoke detected! Gas level: {gas_level} ppm, digital trigger: {digital}"
        elif gas_level >= 500.0:
            return "critical", 82.0, f"High gas levels detected: {gas_level} ppm"
        elif gas_level >= 300.0:
            return "warning", 45.0, f"Elevated gas levels warning: {gas_level} ppm"
        else:
            return "safe", 0.0, f"Smoke and gas levels normal: {gas_level} ppm"

    def evaluate_gyro(self, ax: float, ay: float, az: float) -> Tuple[str, float, str]:
        """Evaluate gyroscope and accelerometer rules (vibration and tilt anomalies).
        
        Returns:
            Tuple of (status, severity, reason)
        """
        # Calculate total acceleration magnitude
        import math
        total_acc = math.sqrt(ax**2 + ay**2 + az**2)
        # Deviation from normal earth gravity (~9.81 m/s^2)
        gravity_deviation = abs(total_acc - 9.81)

        if gravity_deviation >= 8.0:
            return "emergency", 90.0, f"Severe impact or rollover detected! Acc dev: {gravity_deviation:.2f} m/s^2"
        elif gravity_deviation >= 4.0:
            return "critical", 75.0, f"Critical vibration or shock: {gravity_deviation:.2f} m/s^2"
        elif gravity_deviation >= 1.5:
            return "warning", 40.0, f"Mild vibration warning: {gravity_deviation:.2f} m/s^2"
        else:
            return "safe", 0.0, f"Vibration levels normal. Acc dev: {gravity_deviation:.2f} m/s^2"

    def evaluate_brake(self, pressure: float, pad_wear: float) -> Tuple[str, float, str]:
        """Evaluate brake rules.
        
        Returns:
            Tuple of (status, severity, reason)
        """
        if pad_wear >= 90.0:
            return "emergency", 95.0, f"Brake pads fully depleted: {pad_wear}% wear"
        elif pressure > 1800.0 or pressure < 100.0:
            return "critical", 80.0, f"Brake line pressure anomaly: {pressure} psi"
        elif pad_wear >= 75.0:
            return "critical", 70.0, f"High brake pad wear: {pad_wear}% wear"
        elif pad_wear >= 50.0 or pressure > 1400.0:
            return "warning", 45.0, f"Brake maintenance warning. Wear: {pad_wear}%, pressure: {pressure} psi"
        else:
            return "safe", 0.0, f"Brake system operating normally. Wear: {pad_wear}%"
