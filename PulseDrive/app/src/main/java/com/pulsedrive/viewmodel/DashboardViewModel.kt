package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import javax.inject.Inject
import com.pulsedrive.data.repository.DashboardRepository
import com.pulsedrive.data.repository.ServiceConciergeRepository
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class Machine(
    val id: String,
    val name: String,
    val status: String,
    val healthScore: Int,
    val type: String
)

data class DashboardUiState(
    val aiRuntime: String = "Local",
    val esp32Connected: Boolean = true,
    val snapdragonConnected: Boolean = true,
    val inferenceTimeMs: Int = 12,
    val overallHealthScore: Int = 92,
    val remainingUsefulLifeDays: Int = 84,
    val healthStatus: String = "Healthy",
    val diagnosisTitle: String = "Bearing wear detected",
    val diagnosisConfidence: Int = 96,
    val maintenanceTimeline: String = "Maintenance within 48 hrs",
    val temperature: Double = 0.0,
    val voltage: Double = 0.0,
    val lastUpdated: String = "",
    val gpsConnected: Boolean = true,
    val imuConnected: Boolean = true,
    val mpu1Connected: Boolean = true,
    val mpu2Connected: Boolean = true,
    val gasSensorValue: Double = 0.0,
    val gasSensorUnit: String = "ppm",
    val gpsLat: Double? = null,
    val gpsLng: Double? = null,
    val vehiclePredictionLabel: String = "Unknown",
    val vehiclePredictionConfidence: Float = 0f,
    val wheelPredictionLabel: String = "Unknown",
    val wheelPredictionConfidence: Float = 0f,
    val localDiagnosis: String = "Vehicle is operating normally. No abnormalities detected.",
    val localSeverity: String = "Normal",
    val localRecommendation: String = "Continue regular operation. Maintain standard servicing intervals.",
    val machines: List<Machine> = listOf(
        Machine("1", "Main Conveyor Motor", "Healthy", 94, "Conveyor"),
        Machine("2", "Hydraulic Pump B", "Warning", 78, "Hydraulics"),
        Machine("3", "Rotary Compressor 1", "Healthy", 96, "Compressor"),
        Machine("4", "Cooling Fan Alpha", "Healthy", 91, "Cooling")
    )
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: DashboardRepository,
    private val conciergeRepository: ServiceConciergeRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState
 
    init {
        fetchDashboardData()
    }
 
    fun fetchDashboardData() {
        viewModelScope.launch {
            repository.getDashboardData().collect { result ->
                result.fold(
                    onSuccess = { response ->
                        if (response.success) {
                            val data = response.data
                            android.util.Log.d(
                                "DashboardViewModel",
                                "API Telemetry Received -> temp: ${data.temperature}, volt: ${data.voltage}, time: ${data.timestamp}"
                            )
                            
                            val predictions = try {
                                com.pulsedrive.inference.PredictionManager.getInstance().predictAll(response)
                            } catch (e: Exception) {
                                android.util.Log.e("DashboardViewModel", "Prediction failed", e)
                                com.pulsedrive.inference.PredictionBundle(
                                    vehiclePrediction = com.pulsedrive.inference.PredictionResult("Unknown", 0f),
                                    wheelPrediction = com.pulsedrive.inference.PredictionResult("Unknown", 0f)
                                )
                            }

                            val localReport = com.pulsedrive.inference.DiagnosisGenerator.generate(
                                vehicleLabel = predictions.vehiclePrediction.label,
                                vehicleConfidence = predictions.vehiclePrediction.confidence,
                                wheelLabel = predictions.wheelPrediction.label,
                                wheelConfidence = predictions.wheelPrediction.confidence,
                                temperature = data.temperature,
                                voltage = data.voltage,
                                gasValue = data.gasSensor?.value ?: 0.0,
                                gpsConnected = data.gps != null
                            )

                            _uiState.update { currentState ->
                                currentState.copy(
                                    aiRuntime = data.edgeAI.runtime,
                                    esp32Connected = data.connectivity.esp32,
                                    inferenceTimeMs = data.edgeAI.latency,
                                    overallHealthScore = data.healthScore,
                                    remainingUsefulLifeDays = data.remainingUsefulLife,
                                    healthStatus = data.status,
                                    diagnosisTitle = data.aiDiagnosis.message,
                                    diagnosisConfidence = data.aiDiagnosis.confidence,
                                    maintenanceTimeline = data.aiDiagnosis.recommendation,
                                    temperature = data.temperature,
                                    voltage = data.voltage,
                                    lastUpdated = data.timestamp,
                                    gpsConnected = data.gps != null,
                                    imuConnected = data.mpu1 != null || data.mpu2 != null,
                                    mpu1Connected = data.mpu1 != null,
                                    mpu2Connected = data.mpu2 != null,
                                    gasSensorValue = data.gasSensor?.value ?: 0.0,
                                    gasSensorUnit = data.gasSensor?.unit ?: "ppm",
                                    gpsLat = data.gps?.lat,
                                    gpsLng = data.gps?.lng,
                                    vehiclePredictionLabel = predictions.vehiclePrediction.label,
                                    vehiclePredictionConfidence = predictions.vehiclePrediction.confidence,
                                    wheelPredictionLabel = predictions.wheelPrediction.label,
                                    wheelPredictionConfidence = predictions.wheelPrediction.confidence,
                                    localDiagnosis = localReport.diagnosis,
                                    localSeverity = localReport.severity,
                                    localRecommendation = localReport.recommendation
                                )
                            }

                            if (localReport.severity == "Warning" || localReport.severity == "Critical") {
                                viewModelScope.launch {
                                    conciergeRepository.recommendBooking(
                                        vehicleId = "CAR001",
                                        severity = localReport.severity.uppercase(),
                                        phoneNumber = "+919999988888",
                                        fault = localReport.diagnosis
                                    ).collect { recommendResult ->
                                        recommendResult.fold(
                                            onSuccess = { res ->
                                                android.util.Log.d("DashboardViewModel", "Successfully sent alert recommendation to backend: $res")
                                            },
                                            onFailure = { e ->
                                                android.util.Log.e("DashboardViewModel", "Failed to auto-send alert recommendation", e)
                                            }
                                        )
                                    }
                                }
                            }
                        }
                    },
                    onFailure = { error ->
                        android.util.Log.e("DashboardViewModel", "Failed to fetch dashboard data", error)
                    }
                )
            }
        }
    }
}
