package com.pulsedrive.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.pulsedrive.ui.components.GlassmorphicCard
import com.pulsedrive.ui.theme.NearBlack
import com.pulsedrive.ui.theme.TextSecondary
import com.pulsedrive.viewmodel.MaintenanceViewModel
import com.pulsedrive.viewmodel.BookingState
import com.pulsedrive.data.remote.ServiceCenterDto
import com.pulsedrive.data.remote.BookingDto

@Composable
fun MaintenanceScreen(
    viewModel: MaintenanceViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(NearBlack)
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // Title Section
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = "Maintenance Calendar",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            Text(
                text = "Track operations scheduling & AI task allocations",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }

        // Service Concierge Voice Call Alert Dialog
        if (uiState.voiceCallSid != null) {
            AlertDialog(
                onDismissRequest = { viewModel.clearVoiceAlert() },
                confirmButton = {
                    TextButton(onClick = { viewModel.clearVoiceAlert() }) {
                        Text("OK", color = MaterialTheme.colorScheme.primary)
                    }
                },
                title = { Text("AI Concierge Calling", fontWeight = FontWeight.Bold) },
                text = { Text("An outbound telematic concierge call has been initiated. You will receive a call on ${uiState.phoneNumber} shortly to guide you through the booking details.") },
                containerColor = NearBlack,
                titleContentColor = Color.White,
                textContentColor = TextSecondary
            )
        }

        // AI Concierge Booking Stepper Card
        GlassmorphicCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(
                            text = "AI Service Concierge",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = "Outbound call & manual scheduling system",
                            style = MaterialTheme.typography.labelMedium,
                            color = TextSecondary
                        )
                    }
                    if (uiState.bookingState != BookingState.Idle) {
                        IconButton(onClick = { viewModel.cancelBookingFlow() }) {
                            Icon(imageVector = Icons.Default.Close, contentDescription = "Cancel", tint = Color.White)
                        }
                    }
                }

                HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                if (uiState.isLoading) {
                    Box(
                        modifier = Modifier.fillMaxWidth().padding(24.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                    }
                } else {
                    when (uiState.bookingState) {
                        BookingState.Idle -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                Text(
                                    text = "Book vehicle maintenance instantly using the AI voice concierge system or complete step-by-step scheduling manually.",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = TextSecondary
                                )
                                var tempPhone by remember { mutableStateOf("") }
                                OutlinedTextField(
                                    value = tempPhone,
                                    onValueChange = { tempPhone = it },
                                    label = { Text("Driver Phone Number (E.164)", color = TextSecondary) },
                                    placeholder = { Text("+18005550199", color = TextSecondary.copy(alpha = 0.5f)) },
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White,
                                        focusedBorderColor = MaterialTheme.colorScheme.primary,
                                        unfocusedBorderColor = Color(0x33FFFFFF)
                                    ),
                                    modifier = Modifier.fillMaxWidth()
                                )

                                if (uiState.errorMessage != null) {
                                    Text(
                                        text = uiState.errorMessage ?: "",
                                        color = MaterialTheme.colorScheme.error,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Button(
                                        onClick = { viewModel.submitVoiceCall(tempPhone) },
                                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary),
                                        modifier = Modifier.weight(1f),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Icon(imageVector = Icons.Default.Phone, contentDescription = null, modifier = Modifier.size(16.dp))
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("Voice Call", fontWeight = FontWeight.Bold)
                                    }
                                    Button(
                                        onClick = { viewModel.submitPhone(tempPhone, lat = 12.9716, lng = 77.5946) },
                                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
                                        modifier = Modifier.weight(1f),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Text("Manual Book", fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }

                        BookingState.PhoneInput -> {
                            viewModel.cancelBookingFlow()
                        }

                        BookingState.LocationSelect -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Text(
                                    text = "Select Service Center",
                                    style = MaterialTheme.typography.bodyLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = "Choose the nearest authorized repair hub:",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = TextSecondary
                                )

                                uiState.serviceCenters.forEach { center ->
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clip(RoundedCornerShape(10.dp))
                                            .background(Color(0x0CFFFFFF))
                                            .border(1.dp, Color(0x13FFFFFF), RoundedCornerShape(10.dp))
                                            .clickable { viewModel.selectCenter(center) }
                                            .padding(12.dp)
                                    ) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .size(36.dp)
                                                    .background(Color(0x1AFFFFFF), shape = CircleShape),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Icon(imageVector = Icons.Default.LocationOn, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(18.dp))
                                            }
                                            Column(modifier = Modifier.weight(1f)) {
                                                Text(text = center.name, fontWeight = FontWeight.Bold, color = Color.White)
                                                Text(text = center.address, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                                                Text(text = "Hours: ${center.operating_hours}", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                                            }
                                            Icon(imageVector = Icons.Default.ArrowForward, contentDescription = null, tint = TextSecondary, modifier = Modifier.size(16.dp))
                                        }
                                    }
                                }

                                if (uiState.errorMessage != null) {
                                    Text(
                                        text = uiState.errorMessage ?: "",
                                        color = MaterialTheme.colorScheme.error,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                            }
                        }

                        BookingState.DateSelect -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Text(
                                    text = "Select Preferred Date",
                                    style = MaterialTheme.typography.bodyLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = "Selected Center: ${uiState.selectedCenter?.name}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.primary
                                )

                                val dateOptions = listOf("2026-07-20", "2026-07-21", "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-25")
                                Row(
                                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    dateOptions.forEach { date ->
                                        Box(
                                            modifier = Modifier
                                                .clip(RoundedCornerShape(8.dp))
                                                .background(Color(0x0CFFFFFF))
                                                .border(1.dp, Color(0x13FFFFFF), RoundedCornerShape(8.dp))
                                                .clickable { viewModel.selectDate(date) }
                                                .padding(horizontal = 14.dp, vertical = 10.dp)
                                        ) {
                                            Text(text = date, color = Color.White, fontWeight = FontWeight.Bold)
                                        }
                                    }
                                }

                                if (uiState.errorMessage != null) {
                                    Text(
                                        text = uiState.errorMessage ?: "",
                                        color = MaterialTheme.colorScheme.error,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                            }
                        }

                        BookingState.TimeSelect -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Text(
                                    text = "Select Time Slot",
                                    style = MaterialTheme.typography.bodyLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = "Selected Date: ${uiState.selectedDate}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.primary
                                )

                                val slots = uiState.selectedCenter?.available_slots?.ifEmpty {
                                    listOf("09:00", "11:00", "14:00", "16:00")
                                } ?: listOf("09:00", "11:00", "14:00", "16:00")

                                Column(
                                    verticalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    slots.chunked(3).forEach { rowSlots ->
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                                        ) {
                                            rowSlots.forEach { time ->
                                                Box(
                                                    modifier = Modifier
                                                        .weight(1f)
                                                        .clip(RoundedCornerShape(8.dp))
                                                        .background(Color(0x0CFFFFFF))
                                                        .border(1.dp, Color(0x13FFFFFF), RoundedCornerShape(8.dp))
                                                        .clickable { viewModel.selectTimeAndConfirm(time) }
                                                        .padding(vertical = 12.dp),
                                                    contentAlignment = Alignment.Center
                                                ) {
                                                    Text(text = time, color = Color.White, fontWeight = FontWeight.Bold)
                                                }
                                            }
                                            if (rowSlots.size < 3) {
                                                repeat(3 - rowSlots.size) {
                                                    Spacer(modifier = Modifier.weight(1f))
                                                }
                                            }
                                        }
                                    }
                                }

                                if (uiState.errorMessage != null) {
                                    Text(
                                        text = uiState.errorMessage ?: "",
                                        color = MaterialTheme.colorScheme.error,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                            }
                        }

                        BookingState.Confirmed -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(12.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Icon(
                                    imageVector = Icons.Default.CheckCircle,
                                    contentDescription = "Success",
                                    tint = Color(0xFF10B981),
                                    modifier = Modifier.size(48.dp)
                                )
                                Text(
                                    text = "Booking Confirmed!",
                                    style = MaterialTheme.typography.titleLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = "Your appointment has been successfully locked and registered.",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = TextSecondary,
                                    textAlign = TextAlign.Center
                                )

                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .background(Color(0x0CFFFFFF), shape = RoundedCornerShape(10.dp))
                                        .padding(12.dp)
                                ) {
                                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                        Text(text = "Center: ${uiState.selectedCenter?.name}", color = Color.White, fontWeight = FontWeight.Bold)
                                        Text(text = "Address: ${uiState.selectedCenter?.address}", color = TextSecondary, style = MaterialTheme.typography.bodySmall)
                                        Text(text = "Date: ${uiState.selectedDate} | Time: ${uiState.selectedTime}", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                                    }
                                }

                                Button(
                                    onClick = { viewModel.cancelBookingFlow() },
                                    colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                                    modifier = Modifier.fillMaxWidth(),
                                    border = BorderStroke(1.dp, Color(0x33FFFFFF)),
                                    shape = RoundedCornerShape(10.dp)
                                ) {
                                    Text("Back to Maintenance", color = Color.White)
                                }
                            }
                        }
                    }
                }
            }
        }

        // Section 1: Calendar Grid View
        GlassmorphicCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Calendar Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = uiState.currentMonthName,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }

                HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                // Day of Week Labels
                val daysOfWeek = listOf("S", "M", "T", "W", "T", "F", "S")
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceAround
                ) {
                    daysOfWeek.forEach { day ->
                        Text(
                            text = day,
                            modifier = Modifier.width(36.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }

                // Month Calendar Grid (July 2026 starts on Wednesday)
                // Wednesday is the 4th day of the week (indexing 0 for Sunday)
                val startOffset = 3
                val totalDays = 31
                val gridRows = (totalDays + startOffset + 6) / 7

                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    for (row in 0 until gridRows) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceAround
                        ) {
                            for (col in 0 until 7) {
                                val cellIndex = row * 7 + col
                                val dayNumber = cellIndex - startOffset + 1

                                if (dayNumber in 1..totalDays) {
                                    val isHighlighted = uiState.highlightedDays.contains(dayNumber)
                                    Box(
                                        modifier = Modifier
                                            .size(36.dp)
                                            .clip(CircleShape)
                                            .background(
                                                if (isHighlighted) MaterialTheme.colorScheme.primary else Color.Transparent
                                            )
                                            .border(
                                                width = 1.dp,
                                                color = if (isHighlighted) Color.White.copy(alpha = 0.5f) else Color.Transparent,
                                                shape = CircleShape
                                            ),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = dayNumber.toString(),
                                            color = if (isHighlighted) Color.White else TextSecondary,
                                            style = MaterialTheme.typography.bodyMedium,
                                            fontWeight = if (isHighlighted) FontWeight.Bold else FontWeight.Normal
                                        )
                                    }
                                } else {
                                    Spacer(modifier = Modifier.size(36.dp))
                                }
                            }
                        }
                    }
                }
            }
        }

        // Section 3: Upcoming Service Appointments (Booking History)
        if (uiState.bookingHistory.isNotEmpty()) {
            Column(
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text(
                    text = "Upcoming Service Appointments",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )

                uiState.bookingHistory.forEach { booking ->
                    GlassmorphicCard(
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = booking.assigned_service_center ?: "Service Center",
                                    style = MaterialTheme.typography.bodyLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Box(
                                    modifier = Modifier
                                        .background(
                                            when (booking.booking_status) {
                                                "CONFIRMED" -> Color(0x1F10B981)
                                                "CANCELLED" -> Color(0x1FEF5350)
                                                else -> Color(0x1FFFB74D)
                                            },
                                            shape = RoundedCornerShape(6.dp)
                                        )
                                        .padding(horizontal = 8.dp, vertical = 2.dp)
                                ) {
                                    Text(
                                        text = booking.booking_status,
                                        color = when (booking.booking_status) {
                                            "CONFIRMED" -> Color(0xFF10B981)
                                            "CANCELLED" -> Color(0xFFEF5350)
                                            else -> Color(0xFFFFB74D)
                                        },
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                    Text(text = "Booking ID", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                                    Text(text = booking.id ?: "", color = Color.White, style = MaterialTheme.typography.bodyMedium)
                                }
                                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                    Text(text = "Date & Time", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                                    Text(
                                        text = "${booking.preferred_date ?: "-"} @ ${booking.preferred_time ?: "-"}",
                                        color = Color.White,
                                        style = MaterialTheme.typography.bodyMedium
                                    )
                                }
                            }

                            if (booking.booking_status != "CANCELLED") {
                                Button(
                                    onClick = { booking.id?.let { viewModel.cancelBooking(it) } },
                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0x1FEF5350)),
                                    border = BorderStroke(1.dp, Color(0x33EF5350)),
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(8.dp)
                                ) {
                                    Text("Cancel Appointment", color = Color(0xFFEF5350), fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun JobDetailItem(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
    }
}
