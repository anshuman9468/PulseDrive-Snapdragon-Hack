package com.pulsedrive.data.remote

import retrofit2.http.Body
import retrofit2.http.POST

interface AiApi {
    @POST("api/ask-ai")
    suspend fun askAi(@Body request: AskAiRequest): AskAiResponse
}

data class AskAiRequest(
    val question: String
)

data class AskAiResponse(
    val success: Boolean,
    val answer: String
)
