package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pulsedrive.data.repository.MonitorRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ConnectionState(
    val backend: Boolean = false,
    val websocket: Boolean = false,
    val esp32: Boolean = false
)

data class MonitorUiState(
    val temperature: Double = 0.0,
    val voltage: Double = 0.0,
    val mpu1AccX: Double = 0.0,
    val mpu1AccY: Double = 0.0,
    val mpu1AccZ: Double = 0.0,
    val mpu1GyroX: Double = 0.0,
    val mpu1GyroY: Double = 0.0,
    val mpu1GyroZ: Double = 0.0,
    val mpu2AccX: Double = 0.0,
    val mpu2AccY: Double = 0.0,
    val mpu2AccZ: Double = 0.0,
    val mpu2GyroX: Double = 0.0,
    val mpu2GyroY: Double = 0.0,
    val mpu2GyroZ: Double = 0.0,
    val gasSensorValue: Double = 0.0,
    val gasSensorUnit: String = "ppm",
    val gpsLat: Double = 0.0,
    val gpsLng: Double = 0.0,
    val timestamp: String = "",
    val connectionState: ConnectionState = ConnectionState(),
    val signalDataPoints: List<Float> = emptyList()
)

@HiltViewModel
class MonitorViewModel @Inject constructor(
    private val repository: MonitorRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MonitorUiState())
    val uiState: StateFlow<MonitorUiState> = _uiState.asStateFlow()

    private val maxDataPoints = 15

    init {
        startTelemetryPolling()
    }

    private fun startTelemetryPolling() {
        viewModelScope.launch {
            while (true) {
                repository.getLiveTelemetry().collect { result ->
                    result.fold(
                        onSuccess = { response ->
                            if (response.success == true) {
                                val data = response.data
                                _uiState.update { currentState ->
                                    val currentPoints = currentState.signalDataPoints.toMutableList()
                                    if (currentPoints.size >= maxDataPoints) {
                                        currentPoints.removeAt(0)
                                    }
                                    val accZVal = data?.mpu1?.accZ ?: 0.0
                                    currentPoints.add(accZVal.toFloat())

                                    currentState.copy(
                                        temperature = data?.temperature ?: 0.0,
                                        voltage = data?.voltage ?: 0.0,
                                        mpu1AccX = data?.mpu1?.accX ?: 0.0,
                                        mpu1AccY = data?.mpu1?.accY ?: 0.0,
                                        mpu1AccZ = accZVal,
                                        mpu1GyroX = data?.mpu1?.gyroX ?: 0.0,
                                        mpu1GyroY = data?.mpu1?.gyroY ?: 0.0,
                                        mpu1GyroZ = data?.mpu1?.gyroZ ?: 0.0,
                                        mpu2AccX = data?.mpu2?.accX ?: 0.0,
                                        mpu2AccY = data?.mpu2?.accY ?: 0.0,
                                        mpu2AccZ = data?.mpu2?.accZ ?: 0.0,
                                        mpu2GyroX = data?.mpu2?.gyroX ?: 0.0,
                                        mpu2GyroY = data?.mpu2?.gyroY ?: 0.0,
                                        mpu2GyroZ = data?.mpu2?.gyroZ ?: 0.0,
                                        gasSensorValue = data?.gasSensor?.value ?: 0.0,
                                        gasSensorUnit = data?.gasSensor?.unit ?: "ppm",
                                        gpsLat = data?.gps?.lat ?: 0.0,
                                        gpsLng = data?.gps?.lng ?: 0.0,
                                        timestamp = data?.timestamp ?: "",
                                        connectionState = ConnectionState(
                                            backend = true,
                                            websocket = false,
                                            esp32 = false
                                        ),
                                        signalDataPoints = currentPoints
                                    )
                                }
                            }
                        },
                        onFailure = { error ->
                            android.util.Log.e("MonitorViewModel", "Failed to fetch live telemetry", error)
                            _uiState.update { currentState ->
                                currentState.copy(
                                    connectionState = ConnectionState(
                                        backend = false,
                                        websocket = false,
                                        esp32 = false
                                    )
                                )
                            }
                        }
                    )
                }
                delay(2000)
            }
        }
    }
}
