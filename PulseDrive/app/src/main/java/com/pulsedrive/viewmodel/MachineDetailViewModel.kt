package com.pulsedrive.viewmodel

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

data class MetricItem(
    val name: String,
    val value: String,
    val trend: String, // "UP", "DOWN", "STABLE"
    val unit: String
)

data class HistoryItem(
    val date: String,
    val event: String,
    val status: String
)

data class MachineDetailUiState(
    val id: String = "",
    val name: String = "",
    val status: String = "Optimal",
    val healthScore: Int = 94,
    val metrics: List<MetricItem> = emptyList(),
    val predictedFailureMode: String = "None Detected",
    val remainingUsefulLifeDays: Int = 84,
    val history: List<HistoryItem> = emptyList()
)

@HiltViewModel
class MachineDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val machineId: String? = savedStateHandle["machineId"]

    private val _uiState = MutableStateFlow(MachineDetailUiState())
    val uiState: StateFlow<MachineDetailUiState> = _uiState.asStateFlow()

    init {
        loadMachineDetails()
    }

    private fun loadMachineDetails() {
        val id = machineId ?: "1"
        val state = when (id) {
            "2" -> MachineDetailUiState(
                id = "2",
                name = "Hydraulic Pump B",
                status = "Warning",
                healthScore = 78,
                metrics = listOf(
                    MetricItem("Temperature", "74.2", "UP", "°C"),
                    MetricItem("Vibration", "4.8", "UP", "g"),
                    MetricItem("Voltage", "238.4", "STABLE", "V")
                ),
                predictedFailureMode = "Seal leakage risk",
                remainingUsefulLifeDays = 14,
                history = listOf(
                    HistoryItem("2026-07-17", "High vibration detected (4.8g)", "Warning"),
                    HistoryItem("2026-07-15", "Fluid level check complete", "Normal"),
                    HistoryItem("2026-07-10", "Routine lubrication applied", "Normal")
                )
            )
            "3" -> MachineDetailUiState(
                id = "3",
                name = "Rotary Compressor 1",
                status = "Optimal",
                healthScore = 96,
                metrics = listOf(
                    MetricItem("Temperature", "52.8", "STABLE", "°C"),
                    MetricItem("Vibration", "1.2", "DOWN", "g"),
                    MetricItem("Voltage", "240.1", "STABLE", "V")
                ),
                predictedFailureMode = "None Detected",
                remainingUsefulLifeDays = 180,
                history = listOf(
                    HistoryItem("2026-07-01", "Periodic inspection cleared", "Normal")
                )
            )
            "4" -> MachineDetailUiState(
                id = "4",
                name = "Cooling Fan Alpha",
                status = "Optimal",
                healthScore = 91,
                metrics = listOf(
                    MetricItem("Temperature", "41.5", "STABLE", "°C"),
                    MetricItem("Vibration", "2.1", "UP", "g"),
                    MetricItem("Voltage", "239.8", "STABLE", "V")
                ),
                predictedFailureMode = "Blade imbalance warning",
                remainingUsefulLifeDays = 45,
                history = listOf(
                    HistoryItem("2026-07-12", "Fan blade cleaned", "Normal")
                )
            )
            else -> MachineDetailUiState(
                id = "1",
                name = "Main Conveyor Motor",
                status = "Optimal",
                healthScore = 94,
                metrics = listOf(
                    MetricItem("Temperature", "65.4", "STABLE", "°C"),
                    MetricItem("Vibration", "2.4", "DOWN", "g"),
                    MetricItem("Voltage", "239.2", "STABLE", "V")
                ),
                predictedFailureMode = "Bearing wear signature",
                remainingUsefulLifeDays = 84,
                history = listOf(
                    HistoryItem("2026-07-18", "AI diagnostic event: wear detected", "Warning"),
                    HistoryItem("2026-07-05", "Automated oil analysis: pass", "Normal")
                )
            )
        }
        _uiState.value = state
    }
}
