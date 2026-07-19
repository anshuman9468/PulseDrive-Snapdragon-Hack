package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pulsedrive.data.remote.AuthResponse
import com.pulsedrive.data.repository.PulseDriveRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class RegisterUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val registerSuccess: Boolean = false
)

@HiltViewModel
class RegisterViewModel @Inject constructor(
    private val repository: PulseDriveRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState: StateFlow<RegisterUiState> = _uiState.asStateFlow()

    fun register(username: String, email: String, password: String, confirm: String) {
        if (username.isBlank() || email.isBlank() || password.isBlank() || confirm.isBlank()) {
            _uiState.update { it.copy(errorMessage = "All fields are required.") }
            return
        }

        if (password != confirm) {
            _uiState.update { it.copy(errorMessage = "Passwords do not match.") }
            return
        }

        _uiState.update { it.copy(isLoading = true, errorMessage = null) }

        viewModelScope.launch {
            repository.performRegister(username, email, password).collect { result ->
                result.fold(
                    onSuccess = { response ->
                        _uiState.update { it.copy(isLoading = false, registerSuccess = true) }
                    },
                    onFailure = { error ->
                        val displayMsg = error.message ?: "Registration failed."
                        _uiState.update { it.copy(isLoading = false, errorMessage = displayMsg) }
                    }
                )
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    fun resetSuccess() {
        _uiState.update { it.copy(registerSuccess = false) }
    }
}
