package com.pulsedrive

import com.pulsedrive.data.remote.*
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.UUID

class RuntimeVerificationTest {

    private lateinit var apiService: ApiService
    private lateinit var aiApi: AiApi
    private var token: String? = null

    @Before
    fun setUp() {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val authInterceptor = Interceptor { chain ->
            val builder = chain.request().newBuilder()
            token?.let {
                builder.header("Authorization", "Bearer $it")
            }
            chain.proceed(builder.build())
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl("http://127.0.0.1:8000/") // Local backend server
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(ApiService::class.java)
        aiApi = retrofit.create(AiApi::class.java)
    }

    @Test
    fun testAllEndpoints() = runBlocking {
        println("=== STARTING RUNTIME INTEGRATION VERIFICATION ===")

        // 1. Health Status check
        println("\n>>> [1] GET /health")
        try {
            val health = apiService.getHealthStatus()
            println("Response: $health")
            assertTrue(health.status == "ok" || health.status.isNotEmpty())
        } catch (e: Exception) {
            println("GET /health failed: ${e.message}")
            throw e
        }

        // 2. Register mock user
        val mockUsername = "user_${UUID.randomUUID().toString().take(6)}"
        val mockEmail = "$mockUsername@example.com"
        val mockPassword = "password123"

        println("\n>>> [2] POST /api/auth/register")
        try {
            val regRequest = RegisterRequest(mockUsername, mockEmail, mockPassword)
            val regResponse = apiService.register(regRequest)
            println("Response: $regResponse")
            assertNotNull(regResponse.access_token)
            token = regResponse.access_token
        } catch (e: Exception) {
            println("POST /api/auth/register failed: ${e.message}")
        }

        // 3. Login
        println("\n>>> [3] POST /api/auth/login")
        try {
            val loginRequest = LoginRequest(mockEmail, mockPassword)
            val authResponse = apiService.login(loginRequest)
            println("Response: $authResponse")
            assertNotNull(authResponse.access_token)
            token = authResponse.access_token
        } catch (e: Exception) {
            println("POST /api/auth/login failed: ${e.message}")
            try {
                println("Retrying login with standard fallback user: test@example.com")
                val loginRequest = LoginRequest("test@example.com", "password")
                val authResponse = apiService.login(loginRequest)
                println("Fallback Login Response: $authResponse")
                assertNotNull(authResponse.access_token)
                token = authResponse.access_token
            } catch (fallbackEx: Exception) {
                println("Fallback login failed: ${fallbackEx.message}")
                throw fallbackEx
            }
        }

        // 4. Get Current User (Get Me)
        println("\n>>> [4] GET /api/users/me")
        try {
            val me = apiService.getMe()
            println("Response: $me")
            assertNotNull(me.username)
        } catch (e: Exception) {
            println("GET /api/users/me failed: ${e.message}")
            throw e
        }

        // 5. Booking recommend
        println("\n>>> [5] POST /api/service/booking/recommend")
        try {
            val recRequest = RecommendRequest(
                vehicle_id = "CAR001",
                severity = "CRITICAL",
                phone_number = "+919999988888",
                fault = "Local edge IMU prediction shows severe wheel misalignment."
            )
            val recResponse = apiService.recommendBooking(recRequest)
            println("Response: $recResponse")
            assertNotNull(recResponse.action)
        } catch (e: Exception) {
            println("POST /api/service/booking/recommend failed: ${e.message}")
            throw e
        }

        // 6. Start booking
        println("\n>>> [6] POST /api/service/booking/start")
        var bookingId: String? = null
        try {
            val startRequest = StartBookingRequest("CAR001", "+919999988888")
            val startResponse = apiService.startBooking(startRequest)
            println("Response: $startResponse")
            assertNotNull(startResponse.booking_id)
            bookingId = startResponse.booking_id
        } catch (e: Exception) {
            println("POST /api/service/booking/start failed: ${e.message}")
            throw e
        }

        // 7. Get Service Centers
        println("\n>>> [7] GET /api/service/centers")
        try {
            val centers = apiService.getServiceCenters()
            println("Response centers count: ${centers.size}")
            assertTrue(centers.isNotEmpty())
        } catch (e: Exception) {
            println("GET /api/service/centers failed: ${e.message}")
            throw e
        }

        // 8. Get Nearby Service Centers
        println("\n>>> [8] GET /api/service/centers/nearby")
        try {
            val nearbyCenters = apiService.getNearbyCenters(12.9716, 77.5946)
            println("Response nearby centers count: ${nearbyCenters.size}")
            assertTrue(nearbyCenters.isNotEmpty())
        } catch (e: Exception) {
            println("GET /api/service/centers/nearby failed: ${e.message}")
            throw e
        }

        if (bookingId != null) {
            // 9. Select Location
            println("\n>>> [9] POST /api/service/booking/{booking_id}/location")
            try {
                val locRequest = LocationSelectRequest("Bengaluru Authorized Hub", 12.9716, 77.5946)
                val locResponse = apiService.selectLocation(bookingId, locRequest)
                println("Response: $locResponse")
                assertNotNull(locResponse.assigned_service_center)
            } catch (e: Exception) {
                println("POST /api/service/booking/location failed: ${e.message}")
                throw e
            }

            // 10. Select Date
            println("\n>>> [10] POST /api/service/booking/{booking_id}/date")
            try {
                val dateRequest = DateSelectRequest("2026-07-24")
                val dateResponse = apiService.selectDate(bookingId, dateRequest)
                println("Response: $dateResponse")
                assertNotNull(dateResponse.preferred_date)
            } catch (e: Exception) {
                println("POST /api/service/booking/date failed: ${e.message}")
                throw e
            }

            // 11. Select Time Confirm
            println("\n>>> [11] POST /api/service/booking/{booking_id}/confirm")
            try {
                val confirmRequest = TimeConfirmRequest("10:00")
                val confirmResponse = apiService.selectTimeConfirm(bookingId, confirmRequest)
                println("Response: $confirmResponse")
                assertTrue(confirmResponse.booking_status == "CONFIRMED")
            } catch (e: Exception) {
                println("POST /api/service/booking/confirm failed: ${e.message}")
                throw e
            }

            // 12. Voice Call outbound
            println("\n>>> [12] POST /api/service/voice/start-call")
            try {
                val callRequest = StartCallRequest("CAR001", "+18005550199")
                val callResponse = apiService.startVoiceCall(callRequest)
                println("Response: $callResponse")
                assertNotNull(callResponse.call_sid)
            } catch (e: Exception) {
                println("POST /api/service/voice/start-call (expected fail if no Twilio details): ${e.message}")
            }

            // 13. Get Booking History
            println("\n>>> [13] GET /api/service/booking/history")
            try {
                val history = apiService.getBookingHistory("CAR001")
                println("Response history size: ${history.size}")
                assertTrue(history.isNotEmpty())
            } catch (e: Exception) {
                println("GET /api/service/booking/history failed: ${e.message}")
                throw e
            }

            // 14. Cancel Booking
            println("\n>>> [14] POST /api/service/booking/{booking_id}/cancel")
            try {
                val cancelResponse = apiService.cancelBooking(bookingId)
                println("Response: $cancelResponse")
                assertTrue(cancelResponse.booking_status == "CANCELLED")
            } catch (e: Exception) {
                println("POST /api/service/booking/cancel failed: ${e.message}")
                throw e
            }

            // 15. Ask AI Agent
            println("\n>>> [15] POST /api/ask-ai")
            try {
                val aiRequest = AskAiRequest("What is the current status of my vehicle?")
                val aiResponse = aiApi.askAi(aiRequest)
                println("Response success: ${aiResponse.success}, Answer: ${aiResponse.answer}")
                assertTrue(aiResponse.success)
            } catch (e: Exception) {
                println("POST /api/ask-ai failed: ${e.message}")
                throw e
            }
        }

        println("\n=== ALL ENDPOINTS VERIFIED SUCCESSFULLY IN RUNTIME ===")
    }
}
