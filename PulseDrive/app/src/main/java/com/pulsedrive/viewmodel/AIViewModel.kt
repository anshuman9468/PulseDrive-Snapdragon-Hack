package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

data class PipelineStep(
    val stage: String,
    val title: String,
    val description: String,
    val status: String // e.g. "Completed", "Active", "Pending"
)

data class AiUiState(
    val modelName: String = "RandomForest.onnx",
    val runtime: String = "ONNX Runtime",
    val inference: String = "Local",
    val latencyMs: Int = 11,
    val cpuUsagePercent: Int = 18,
    val cloudUsagePercent: Int = 0,
    val optimizationStatus: String = "Optimized using Qualcomm AI Hub",
    val steps: List<PipelineStep> = listOf(
        PipelineStep("1", "Prediction", "Bearing failure likely in 4 days", "Active"),
        PipelineStep("2", "Diagnosis", "Vibration pattern matches bearing wear signature", "Active"),
        PipelineStep("3", "Recommendation", "Schedule replacement within 48 hrs", "Active")
    )
)

@HiltViewModel
class AIViewModel @Inject constructor() : ViewModel() {
    private val _uiState = MutableStateFlow(AiUiState())
    val uiState: StateFlow<AiUiState> = _uiState.asStateFlow()
}
