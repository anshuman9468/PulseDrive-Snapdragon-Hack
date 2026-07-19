package com.pulsedrive.data.repository

import com.pulsedrive.data.remote.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

interface ServiceConciergeRepository {
    fun startBooking(vehicleId: String, phoneNumber: String): Flow<Result<StartBookingResponse>>
    fun selectLocation(bookingId: String, location: String, latitude: Double, longitude: Double): Flow<Result<LocationSelectResponse>>
    fun selectDate(bookingId: String, date: String): Flow<Result<DateSelectResponse>>
    fun selectTimeConfirm(bookingId: String, time: String): Flow<Result<TimeConfirmResponse>>
    fun cancelBooking(bookingId: String): Flow<Result<CancelBookingResponse>>
    fun getBookingHistory(vehicleId: String?): Flow<Result<List<BookingDto>>>
    fun getServiceCenters(): Flow<Result<List<ServiceCenterDto>>>
    fun getNearbyCenters(lat: Double, lng: Double): Flow<Result<List<ServiceCenterDto>>>
    fun startVoiceCall(vehicleId: String, phoneNumber: String): Flow<Result<StartCallResponse>>
    fun recommendBooking(vehicleId: String, severity: String, phoneNumber: String, fault: String): Flow<Result<RecommendResponse>>
}

@Singleton
class ServiceConciergeRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : ServiceConciergeRepository {
    override fun startBooking(vehicleId: String, phoneNumber: String): Flow<Result<StartBookingResponse>> = flow {
        try {
            emit(Result.success(apiService.startBooking(StartBookingRequest(vehicleId, phoneNumber))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun selectLocation(bookingId: String, location: String, latitude: Double, longitude: Double): Flow<Result<LocationSelectResponse>> = flow {
        try {
            emit(Result.success(apiService.selectLocation(bookingId, LocationSelectRequest(location, latitude, longitude))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun selectDate(bookingId: String, date: String): Flow<Result<DateSelectResponse>> = flow {
        try {
            emit(Result.success(apiService.selectDate(bookingId, DateSelectRequest(date))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun selectTimeConfirm(bookingId: String, time: String): Flow<Result<TimeConfirmResponse>> = flow {
        try {
            emit(Result.success(apiService.selectTimeConfirm(bookingId, TimeConfirmRequest(time))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun cancelBooking(bookingId: String): Flow<Result<CancelBookingResponse>> = flow {
        try {
            emit(Result.success(apiService.cancelBooking(bookingId)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun getBookingHistory(vehicleId: String?): Flow<Result<List<BookingDto>>> = flow {
        try {
            emit(Result.success(apiService.getBookingHistory(vehicleId)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun getServiceCenters(): Flow<Result<List<ServiceCenterDto>>> = flow {
        try {
            emit(Result.success(apiService.getServiceCenters()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun getNearbyCenters(lat: Double, lng: Double): Flow<Result<List<ServiceCenterDto>>> = flow {
        try {
            emit(Result.success(apiService.getNearbyCenters(lat, lng)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun startVoiceCall(vehicleId: String, phoneNumber: String): Flow<Result<StartCallResponse>> = flow {
        try {
            emit(Result.success(apiService.startVoiceCall(StartCallRequest(vehicleId, phoneNumber))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun recommendBooking(vehicleId: String, severity: String, phoneNumber: String, fault: String): Flow<Result<RecommendResponse>> = flow {
        try {
            emit(Result.success(apiService.recommendBooking(RecommendRequest(vehicleId, severity, phoneNumber, fault))))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
