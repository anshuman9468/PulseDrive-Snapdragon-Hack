package com.pulsedrive.data.repository

import com.pulsedrive.data.remote.AiApi
import com.pulsedrive.data.remote.AskAiRequest
import retrofit2.HttpException
import java.io.IOException
import java.net.SocketTimeoutException
import javax.inject.Inject
import javax.inject.Singleton

interface AiRepository {
    suspend fun askQuestion(question: String): Result<String>
}

@Singleton
class AiRepositoryImpl @Inject constructor(
    private val aiApi: AiApi
) : AiRepository {
    override suspend fun askQuestion(question: String): Result<String> {
        return try {
            val response = aiApi.askAi(AskAiRequest(question))
            if (response.success) {
                Result.success(response.answer)
            } else {
                Result.failure(Exception("AI Assistant failed to generate an answer."))
            }
        } catch (e: SocketTimeoutException) {
            Result.failure(Exception("Request timed out. Please check your connection and try again."))
        } catch (e: IOException) {
            Result.failure(Exception("Network unavailable. Please check your internet connection."))
        } catch (e: HttpException) {
            val errorMsg = when (e.code()) {
                500 -> "Internal server error. Please try again later."
                404 -> "Server endpoint not found."
                else -> "Server error (${e.code()}). Please try again."
            }
            Result.failure(Exception(errorMsg))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
