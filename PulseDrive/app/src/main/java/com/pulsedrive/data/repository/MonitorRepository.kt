package com.pulsedrive.data.repository

import android.util.Log
import com.pulsedrive.data.remote.LiveTelemetryResponse
import com.pulsedrive.data.remote.MonitorApiService
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

interface MonitorRepository {
    fun getLiveTelemetry(): Flow<Result<LiveTelemetryResponse>>
}

@Singleton
class MonitorRepositoryImpl @Inject constructor(
    private val apiService: MonitorApiService
) : MonitorRepository {
    override fun getLiveTelemetry(): Flow<Result<LiveTelemetryResponse>> = flow {
        Log.d("MonitorRepository", "API request initiated to GET /api/live")
        val response = apiService.getLiveTelemetry()
        Log.d("MonitorRepository", "API response received successfully: $response")
        emit(response)
    }.map {
        Result.success(it)
    }.catch { e ->
        Log.e("MonitorRepository", "Live telemetry API failed", e)
        emit(Result.failure(e))
    }
}
