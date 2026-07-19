package com.pulsedrive.data.remote

import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Path
import retrofit2.http.Query
import com.google.gson.annotations.SerializedName

interface ApiService {
    @GET("health")
    suspend fun getHealthStatus(): HealthStatusResponse

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("api/auth/register")
    suspend fun register(@Body request: RegisterRequest): AuthResponse

    @GET("api/users/me")
    suspend fun getMe(): UserResponse

    // New Service Concierge Routes
    @POST("api/service/booking/recommend")
    suspend fun recommendBooking(@Body request: RecommendRequest): RecommendResponse

    @POST("api/service/voice/start-call")
    suspend fun startVoiceCall(@Body request: StartCallRequest): StartCallResponse

    @GET("api/service/booking/history")
    suspend fun getBookingHistory(@Query("vehicle_id") vehicleId: String?): List<BookingDto>

    @POST("api/service/booking/start")
    suspend fun startBooking(@Body request: StartBookingRequest): StartBookingResponse

    @POST("api/service/booking/{booking_id}/location")
    suspend fun selectLocation(
        @Path("booking_id") bookingId: String,
        @Body request: LocationSelectRequest
    ): LocationSelectResponse

    @POST("api/service/booking/{booking_id}/date")
    suspend fun selectDate(
        @Path("booking_id") bookingId: String,
        @Body request: DateSelectRequest
    ): DateSelectResponse

    @POST("api/service/booking/{booking_id}/confirm")
    suspend fun selectTimeConfirm(
        @Path("booking_id") bookingId: String,
        @Body request: TimeConfirmRequest
    ): TimeConfirmResponse

    @POST("api/service/booking/{booking_id}/cancel")
    suspend fun cancelBooking(@Path("booking_id") bookingId: String): CancelBookingResponse

    @GET("api/service/centers")
    suspend fun getServiceCenters(): List<ServiceCenterDto>

    @GET("api/service/centers/nearby")
    suspend fun getNearbyCenters(
        @Query("lat") lat: Double,
        @Query("lng") lng: Double
    ): List<ServiceCenterDto>
}

data class HealthStatusResponse(val status: String, val edgeAiActive: Boolean? = null)

data class LoginRequest(val email: String, val password: String)

data class RegisterRequest(val username: String, val email: String, val password: String)

data class UserResponse(val id: String, val username: String, val email: String)

data class AuthResponse(
    val access_token: String,
    val token_type: String?,
    val user: UserResponse?
)

data class StartCallRequest(
    @SerializedName("vehicle_id") val vehicle_id: String,
    @SerializedName("phone_number") val phone_number: String
)

data class StartCallResponse(
    val status: String,
    @SerializedName("call_sid") val call_sid: String,
    @SerializedName("phone_number") val phone_number: String
)

data class BookingDto(
    @SerializedName("booking_id") val id: String?,
    val vehicle_id: String,
    val customer_name: String?,
    val phone_number: String,
    val location: String?,
    val latitude: Double?,
    val longitude: Double?,
    val preferred_date: String?,
    val preferred_time: String?,
    val assigned_service_center: String?,
    @SerializedName("status") val booking_status: String,
    val decision_severity: String?
)

data class StartBookingRequest(val vehicle_id: String, val phone_number: String)
data class StartBookingResponse(val status: String, val booking_id: String, val state: String)

data class LocationSelectRequest(val location: String, val latitude: Double, val longitude: Double)
data class LocationSelectResponse(val status: String, val booking_id: String, val assigned_service_center: String?)

data class DateSelectRequest(val date: String)
data class DateSelectResponse(val status: String, val booking_id: String, val preferred_date: String?)

data class TimeConfirmRequest(val time: String)
data class TimeConfirmResponse(
    val status: String,
    val booking_id: String,
    val booking_status: String,
    val assigned_service_center: String?,
    val date: String?,
    val time: String?
)

data class CancelBookingResponse(val status: String, val booking_id: String, val booking_status: String)

data class ServiceCenterDto(
    val id: String?,
    val name: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val phone_number: String,
    val operating_hours: String,
    val available_slots: List<String>
)

data class RecommendRequest(
    val vehicle_id: String,
    val severity: String,
    val phone_number: String,
    val fault: String
)

data class RecommendResponse(
    val action: String,
    val booking_id: String?,
    val severity: String?
)
