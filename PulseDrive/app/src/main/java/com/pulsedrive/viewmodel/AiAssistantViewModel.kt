package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pulsedrive.data.repository.AiRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AiChatMessage(
    val text: String,
    val isUser: Boolean,
    val timestamp: Long
)

data class AiAssistantUiState(
    val messages: List<AiChatMessage> = emptyList(),
    val currentInput: String = "",
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class AiAssistantViewModel @Inject constructor(
    private val repository: AiRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AiAssistantUiState())
    val uiState: StateFlow<AiAssistantUiState> = _uiState.asStateFlow()

    private var lastSentQuestion: String? = null

    init {
        _uiState.update { currentState ->
            currentState.copy(
                messages = listOf(
                    AiChatMessage(
                        text = "Hello! I am your PulseDrive Vehicle Health Assistant. How can I help you today?",
                        isUser = false,
                        timestamp = System.currentTimeMillis()
                    )
                )
            )
        }
    }

    fun updateInput(input: String) {
        _uiState.update { it.copy(currentInput = input) }
    }

    fun sendMessage(question: String = _uiState.value.currentInput) {
        if (question.isBlank()) return

        val userMessage = AiChatMessage(
            text = question,
            isUser = true,
            timestamp = System.currentTimeMillis()
        )

        lastSentQuestion = question

        _uiState.update { currentState ->
            currentState.copy(
                messages = currentState.messages + userMessage,
                currentInput = if (question == currentState.currentInput) "" else currentState.currentInput,
                isLoading = true,
                error = null
            )
        }

        viewModelScope.launch {
            val result = repository.askQuestion(question)
            result.fold(
                onSuccess = { answer ->
                    _uiState.update { currentState ->
                        currentState.copy(
                            messages = currentState.messages + AiChatMessage(
                                text = answer,
                                isUser = false,
                                timestamp = System.currentTimeMillis()
                            ),
                            isLoading = false
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update { currentState ->
                        currentState.copy(
                            isLoading = false,
                            error = error.message ?: "Failed to get response."
                        )
                    }
                }
            )
        }
    }

    fun retryLastMessage() {
        lastSentQuestion?.let {
            sendMessage(it)
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
