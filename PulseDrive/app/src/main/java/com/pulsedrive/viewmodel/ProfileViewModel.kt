package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pulsedrive.data.repository.PulseDriveRepository
import com.pulsedrive.utils.SessionManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProfileUiState(
    val username: String = "",
    val email: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val logoutSuccess: Boolean = false
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: PulseDriveRepository,
    private val sessionManager: SessionManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadUserProfile()
    }

    fun loadUserProfile() {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        viewModelScope.launch {
            repository.fetchUserProfile().collect { result ->
                result.fold(
                    onSuccess = { response ->
                        sessionManager.saveUserSession(response.email, response.username)
                        _uiState.update { currentState ->
                            currentState.copy(
                                username = response.username,
                                email = response.email,
                                isLoading = false
                            )
                        }
                    },
                    onFailure = { error ->
                        val savedEmail = sessionManager.getUserEmail() ?: ""
                        val savedName = sessionManager.getUserName() ?: ""
                        _uiState.update { currentState ->
                            currentState.copy(
                                username = savedName.ifEmpty { "Operator" },
                                email = savedEmail.ifEmpty { "offline@pulsedrive.io" },
                                isLoading = false,
                                errorMessage = error.message
                            )
                        }
                    }
                )
            }
        }
    }

    fun logout() {
        sessionManager.clearSession()
        _uiState.update { it.copy(logoutSuccess = true) }
    }
}
