package com.pulsedrive.viewmodel

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

enum class NotificationType {
    CRITICAL,
    MAINTENANCE,
    ENGINEER,
    CALL
}

data class NotificationItem(
    val id: String,
    val type: NotificationType,
    val title: String,
    val description: String,
    val timestamp: String,
    val isUnread: Boolean
)

data class NotificationsUiState(
    val notifications: List<NotificationItem> = listOf(
        NotificationItem(
            id = "n-1",
            type = NotificationType.CRITICAL,
            title = "Critical Alert",
            description = "Bearing wear detected — confidence 96%",
            timestamp = "10 mins ago",
            isUnread = true
        ),
        NotificationItem(
            id = "n-2",
            type = NotificationType.CALL,
            title = "Call Triggered",
            description = "AI Agent placed an automated call to engineer at 10:42 AM",
            timestamp = "15 mins ago",
            isUnread = true
        ),
        NotificationItem(
            id = "n-3",
            type = NotificationType.ENGINEER,
            title = "Engineer Assigned",
            description = "Technician Raj assigned to Motor Conveyor #3",
            timestamp = "1 hour ago",
            isUnread = false
        ),
        NotificationItem(
            id = "n-4",
            type = NotificationType.MAINTENANCE,
            title = "Maintenance Scheduled",
            description = "Auto-scheduled by AI Agent for July 20",
            timestamp = "2 hours ago",
            isUnread = false
        )
    )
)

@HiltViewModel
class NotificationsViewModel @Inject constructor() : ViewModel() {
    private val _uiState = MutableStateFlow(NotificationsUiState())
    val uiState: StateFlow<NotificationsUiState> = _uiState.asStateFlow()

    fun markAllAsRead() {
        _uiState.value = _uiState.value.copy(
            notifications = _uiState.value.notifications.map { it.copy(isUnread = false) }
        )
    }
}
