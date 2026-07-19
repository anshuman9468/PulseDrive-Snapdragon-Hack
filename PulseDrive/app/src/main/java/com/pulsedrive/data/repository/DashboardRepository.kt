package com.pulsedrive.data.repository

import com.pulsedrive.data.remote.DashboardApiService
import com.pulsedrive.data.remote.DashboardResponse
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

import android.util.Log

interface DashboardRepository {
    fun getDashboardData(): Flow<Result<DashboardResponse>>
}

@Singleton
class DashboardRepositoryImpl @Inject constructor(
    private val apiService: DashboardApiService
) : DashboardRepository {
    override fun getDashboardData(): Flow<Result<DashboardResponse>> = flow {
        try {
            Log.d("DashboardRepository", "API request initiated to GET /api/dashboard")
            val response = apiService.getDashboardData()
            Log.d("DashboardRepository", "API response received successfully: $response")
            emit(Result.success(response))
        } catch (e: Exception) {
            Log.e(
                "DashboardRepository",
                "Dashboard API failed",
                e
            )
            emit(Result.failure(e))
        }
    }
}
