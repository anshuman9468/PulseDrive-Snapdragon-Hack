package com.pulsedrive.data.repository

import com.pulsedrive.data.remote.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PulseDriveRepository @Inject constructor(
    private val apiService: ApiService
) {
    fun performLogin(email: String, password: String): Flow<Result<AuthResponse>> = flow {
        try {
            val response = apiService.login(LoginRequest(email, password))
            emit(Result.success(response))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun performRegister(username: String, email: String, password: String): Flow<Result<AuthResponse>> = flow {
        try {
            val response = apiService.register(RegisterRequest(username, email, password))
            emit(Result.success(response))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    fun fetchUserProfile(): Flow<Result<UserResponse>> = flow {
        try {
            val response = apiService.getMe()
            emit(Result.success(response))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
