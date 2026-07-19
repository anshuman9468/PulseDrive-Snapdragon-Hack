package com.pulsedrive.data.remote

import retrofit2.http.GET

interface MonitorApiService {
    @GET("api/live")
    suspend fun getLiveTelemetry(): LiveTelemetryResponse
}

data class LiveTelemetryResponse(
    val success: Boolean?,
    val data: LiveTelemetryData?
)

data class LiveTelemetryData(
    val vehicleId: String?,
    val temperature: Double?,
    val voltage: Double?,
    val gps: GpsDto?,
    val mpu1: MpuDataDto?,
    val mpu2: MpuDataDto?,
    val gasSensor: GasSensorDto?,
    val timestamp: String?
)
