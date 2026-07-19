package com.pulsedrive.inference

data class DiagnosisReport(
    val diagnosis: String,
    val severity: String, // "Normal", "Warning", "Critical"
    val recommendation: String
)

object DiagnosisGenerator {

    /**
     * Generates a local diagnosis report based on vehicle predictions, wheel predictions,
     * temperature, voltage, gas sensor values, and GPS connectivity.
     */
    fun generate(
        vehicleLabel: String,
        vehicleConfidence: Float,
        wheelLabel: String,
        wheelConfidence: Float,
        temperature: Double,
        voltage: Double,
        gasValue: Double,
        gpsConnected: Boolean
    ): DiagnosisReport {
        // High temp threshold: 42.0 °C
        val isHighTemp = temperature >= 42.0
        // Low voltage threshold: 11.8 V
        val isLowVoltage = voltage <= 11.8
        // High gas threshold: 300.0 ppm
        val isHighGas = gasValue >= 300.0

        return when {
            // Case 3: High Temperature & Low Voltage
            isHighTemp && isLowVoltage -> {
                DiagnosisReport(
                    diagnosis = "Engine temperature is abnormally high and battery voltage is low. Immediate inspection is recommended.",
                    severity = "Critical",
                    recommendation = "Check radiator cooling and alternator terminals immediately."
                )
            }
            // Critical Gas Leak
            isHighGas -> {
                DiagnosisReport(
                    diagnosis = "Hazardous gas concentration detected in engine compartment ($gasValue ppm). Exhaust or fuel leak suspected.",
                    severity = "Critical",
                    recommendation = "Shut down the engine and inspect fuel lines and exhaust manifold."
                )
            }
            // Critical Temperature
            isHighTemp -> {
                DiagnosisReport(
                    diagnosis = "Engine temperature is abnormally high ($temperature °C). Cooling system failure suspected.",
                    severity = "Critical",
                    recommendation = "Inspect cooling fan operation and engine coolant levels."
                )
            }
            // Case 2: Wheel Imbalance
            wheelLabel == "Imbalance" && wheelConfidence >= 0.5f -> {
                val confidencePct = (wheelConfidence * 100).toInt()
                DiagnosisReport(
                    diagnosis = "Wheel imbalance detected with high confidence ($confidencePct%). Suspension and wheel alignment inspection is recommended.",
                    severity = "Warning",
                    recommendation = "Schedule wheel balancing and suspension calibration."
                )
            }
            // Warning Low Voltage
            isLowVoltage -> {
                DiagnosisReport(
                    diagnosis = "Battery voltage is low ($voltage V). Alternator efficiency may be compromised.",
                    severity = "Warning",
                    recommendation = "Test battery charging capacity and check alternator belt."
                )
            }
            // Warning GPS Signal Lost
            !gpsConnected -> {
                DiagnosisReport(
                    diagnosis = "GPS telemetry is currently offline. Location tracking and services are unavailable.",
                    severity = "Warning",
                    recommendation = "Verify GPS module antenna placement and connections."
                )
            }
            // Case 1: Normal Operation
            else -> {
                DiagnosisReport(
                    diagnosis = "Vehicle is operating normally. No abnormalities detected.",
                    severity = "Normal",
                    recommendation = "Continue regular operation. Maintain standard servicing intervals."
                )
            }
        }
    }
}
