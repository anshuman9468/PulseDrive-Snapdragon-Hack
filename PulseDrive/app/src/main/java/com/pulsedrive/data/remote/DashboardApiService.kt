package com.pulsedrive.data.remote

import retrofit2.http.GET

interface DashboardApiService {
    @GET("api/dashboard")
    suspend fun getDashboardData(): DashboardResponse
}

data class DashboardResponse(
    val success: Boolean,
    val data: DashboardData
)

data class DashboardData(
    val vehicleId: String,
    val temperature: Double,
    val voltage: Double,
    val gps: GpsDto?,
    val mpu1: MpuDataDto?,
    val mpu2: MpuDataDto?,
    val gasSensor: GasSensorDto?,
    val timestamp: String,
    val healthScore: Int,
    val status: String,
    val remainingUsefulLife: Int,
    val aiDiagnosis: AiDiagnosisDto,
    val edgeAI: EdgeAiDto,
    val connectivity: ConnectivityDto
)

data class GpsDto(
    val lat: Double,
    val lng: Double
)

data class MpuDataDto(
    val accX: Double,
    val accY: Double,
    val accZ: Double,
    val gyroX: Double,
    val gyroY: Double,
    val gyroZ: Double
)

data class GasSensorDto(
    val value: Double,
    val unit: String
)

data class AiDiagnosisDto(
    val message: String,
    val confidence: Int,
    val recommendation: String
)

data class EdgeAiDto(
    val runtime: String,
    val latency: Int,
    val status: String
)

data class ConnectivityDto(
    val esp32: Boolean,
    val websocket: Boolean
)
