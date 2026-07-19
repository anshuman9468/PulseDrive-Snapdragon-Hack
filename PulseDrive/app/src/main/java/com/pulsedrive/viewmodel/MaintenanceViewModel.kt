package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pulsedrive.data.remote.BookingDto
import com.pulsedrive.data.remote.ServiceCenterDto
import com.pulsedrive.data.repository.ServiceConciergeRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class BookingState {
    Idle,
    PhoneInput,
    LocationSelect,
    DateSelect,
    TimeSelect,
    Confirmed
}

data class MaintenanceTask(
    val id: String,
    val machineName: String,
    val date: String,
    val technician: String,
    val cost: String,
    val partsNeeded: List<String>,
    val isAutoScheduled: Boolean = true
)

data class MaintenanceUiState(
    val currentMonthName: String = "July 2026",
    val highlightedDays: List<Int> = listOf(12, 19, 24), // Days with scheduled maintenance
    val nextTask: MaintenanceTask = MaintenanceTask(
        id = "M-9482",
        machineName = "Conveyor Motor Alpha",
        date = "July 24, 2026",
        technician = "John Doe (Senior Mechanical Engineer)",
        cost = "$350.00",
        partsNeeded = listOf(
            "Ball Bearing Model SKF-6204",
            "Premium Synthetic Lubricant",
            "Industrial Seal Ring"
        )
    ),
    // Concierge state properties
    val bookingState: BookingState = BookingState.Idle,
    val bookingId: String? = null,
    val phoneNumber: String = "",
    val serviceCenters: List<ServiceCenterDto> = emptyList(),
    val selectedCenter: ServiceCenterDto? = null,
    val selectedDate: String? = null,
    val selectedTime: String? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val bookingHistory: List<BookingDto> = emptyList(),
    val voiceCallSid: String? = null
)

@HiltViewModel
class MaintenanceViewModel @Inject constructor(
    private val repository: ServiceConciergeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MaintenanceUiState())
    val uiState: StateFlow<MaintenanceUiState> = _uiState.asStateFlow()

    init {
        loadBookingHistory()
    }

    fun loadBookingHistory(vehicleId: String? = "CAR001") {
        viewModelScope.launch {
            repository.getBookingHistory(vehicleId).collect { result ->
                result.fold(
                    onSuccess = { history ->
                        _uiState.update { it.copy(bookingHistory = history) }
                    },
                    onFailure = { e ->
                        android.util.Log.e("MaintenanceVM", "Failed to fetch booking history", e)
                    }
                )
            }
        }
    }

    fun startBookingFlow() {
        _uiState.update { it.copy(bookingState = BookingState.PhoneInput, errorMessage = null) }
    }

    fun cancelBookingFlow() {
        _uiState.update { 
            it.copy(
                bookingState = BookingState.Idle,
                bookingId = null,
                selectedCenter = null,
                selectedDate = null,
                selectedTime = null,
                errorMessage = null
            ) 
        }
    }

    fun submitPhone(phoneNumber: String, vehicleId: String = "CAR001", lat: Double? = null, lng: Double? = null) {
        if (phoneNumber.isBlank()) {
            _uiState.update { it.copy(errorMessage = "Phone number cannot be empty.") }
            return
        }
        val cleanPhone = phoneNumber.trim()
        val formattedPhone = if (cleanPhone.startsWith("+")) cleanPhone else "+$cleanPhone"
        _uiState.update { it.copy(isLoading = true, errorMessage = null, phoneNumber = formattedPhone) }
        viewModelScope.launch {
            repository.startBooking(vehicleId, formattedPhone).collect { result ->
                result.fold(
                    onSuccess = { response ->
                        val bId = response.booking_id
                        // Query nearby centers if coordinates are present, otherwise load all
                        val centersFlow = if (lat != null && lng != null) {
                            repository.getNearbyCenters(lat, lng)
                        } else {
                            repository.getServiceCenters()
                        }
                        
                        centersFlow.collect { centersResult ->
                            centersResult.fold(
                                onSuccess = { centers ->
                                    if (centers.isEmpty() && lat != null && lng != null) {
                                        // Fallback to all centers if nearby query yielded none
                                        repository.getServiceCenters().collect { fallbackResult ->
                                            fallbackResult.fold(
                                                onSuccess = { allCenters ->
                                                    _uiState.update {
                                                        it.copy(
                                                            isLoading = false,
                                                            bookingId = bId,
                                                            serviceCenters = allCenters,
                                                            bookingState = BookingState.LocationSelect
                                                        )
                                                    }
                                                },
                                                onFailure = { e ->
                                                    _uiState.update {
                                                        it.copy(
                                                            isLoading = false,
                                                            errorMessage = "Failed to load fallback service centers: ${e.message}"
                                                        )
                                                    }
                                                }
                                            )
                                        }
                                    } else {
                                        _uiState.update {
                                            it.copy(
                                                isLoading = false,
                                                bookingId = bId,
                                                serviceCenters = centers,
                                                bookingState = BookingState.LocationSelect
                                            )
                                        }
                                    }
                                },
                                onFailure = { e ->
                                    // Fallback to all centers on error
                                    repository.getServiceCenters().collect { fallbackResult ->
                                        fallbackResult.fold(
                                            onSuccess = { allCenters ->
                                                _uiState.update {
                                                    it.copy(
                                                        isLoading = false,
                                                        bookingId = bId,
                                                        serviceCenters = allCenters,
                                                        bookingState = BookingState.LocationSelect
                                                    )
                                                }
                                            },
                                            onFailure = { fallbackErr ->
                                                _uiState.update {
                                                    it.copy(
                                                        isLoading = false,
                                                        errorMessage = "Failed to load service centers: ${fallbackErr.message}"
                                                    )
                                                }
                                            }
                                        )
                                    }
                                }
                            )
                        }
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to initiate booking: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }

    fun submitVoiceCall(phoneNumber: String, vehicleId: String = "CAR001") {
        if (phoneNumber.isBlank()) {
            _uiState.update { it.copy(errorMessage = "Phone number cannot be empty.") }
            return
        }
        val cleanPhone = phoneNumber.trim()
        val formattedPhone = if (cleanPhone.startsWith("+")) cleanPhone else "+$cleanPhone"
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.startVoiceCall(vehicleId, formattedPhone).collect { result ->
                result.fold(
                    onSuccess = { response ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                voiceCallSid = response.call_sid,
                                errorMessage = null
                            )
                        }
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to initiate voice concierge call: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }

    fun clearVoiceAlert() {
        _uiState.update { it.copy(voiceCallSid = null) }
    }

    fun selectCenter(center: ServiceCenterDto) {
        val bId = _uiState.value.bookingId ?: return
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.selectLocation(bId, center.name, center.latitude, center.longitude).collect { result ->
                result.fold(
                    onSuccess = {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                selectedCenter = center,
                                bookingState = BookingState.DateSelect
                            )
                        }
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to select location center: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }

    fun selectDate(date: String) {
        val bId = _uiState.value.bookingId ?: return
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.selectDate(bId, date).collect { result ->
                result.fold(
                    onSuccess = {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                selectedDate = date,
                                bookingState = BookingState.TimeSelect
                            )
                        }
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to select preferred date: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }

    fun selectTimeAndConfirm(time: String) {
        val bId = _uiState.value.bookingId ?: return
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.selectTimeConfirm(bId, time).collect { result ->
                result.fold(
                    onSuccess = {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                selectedTime = time,
                                bookingState = BookingState.Confirmed
                            )
                        }
                        loadBookingHistory()
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to confirm appointment booking: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }

    fun cancelBooking(bookingId: String) {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.cancelBooking(bookingId).collect { result ->
                result.fold(
                    onSuccess = {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                bookingState = BookingState.Idle,
                                bookingId = null,
                                selectedCenter = null,
                                selectedDate = null,
                                selectedTime = null
                            )
                        }
                        loadBookingHistory()
                    },
                    onFailure = { e ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                errorMessage = "Failed to cancel booking appointment: ${e.message}"
                            )
                        }
                    }
                )
            }
        }
    }
}
