package com.pulsedrive.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.pulsedrive.ui.components.GlassmorphicCard
import com.pulsedrive.ui.theme.GreenStatus
import com.pulsedrive.ui.theme.NearBlack
import com.pulsedrive.ui.theme.TextSecondary
import com.pulsedrive.viewmodel.DashboardViewModel
import com.pulsedrive.viewmodel.Machine
import kotlinx.coroutines.launch

@Composable
fun DashboardScreen(
    onMachineClick: (String) -> Unit,
    onMaintenanceClick: () -> Unit = {},
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    android.util.Log.d("DashboardScreen", "Recomposition triggered: uiState = $uiState")
    val scrollState = rememberScrollState()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = NearBlack
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(scrollState)
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // 1. Top bar / status row (horizontal row, visible immediately without scrolling)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                StatusBadge(text = "AI Runtime: 🟢 ${uiState.aiRuntime}")
                StatusBadge(text = "ESP32: ${if (uiState.esp32Connected) "🟢 Connected" else "🔴 Disconnected"}")
                StatusBadge(text = "Snapdragon: ${if (uiState.snapdragonConnected) "🟢 Connected" else "🔴 Disconnected"}")
                StatusBadge(text = "Inference: ${uiState.inferenceTimeMs} ms")
            }

            // 2. Center hero card (Machine Health -> Vehicle State)
            GlassmorphicCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Vehicle State",
                            style = MaterialTheme.typography.titleMedium,
                            color = TextSecondary,
                            fontWeight = FontWeight.Bold
                        )
                        Box(
                            modifier = Modifier
                                .background(Color(0x1F3B82F6), shape = RoundedCornerShape(8.dp))
                                .border(1.dp, Color(0x333B82F6), shape = RoundedCornerShape(8.dp))
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = uiState.vehiclePredictionLabel.ifEmpty { "Unknown" },
                                color = MaterialTheme.colorScheme.primary,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Circular / Radial Glow Health Ring Representation (Vehicle Confidence)
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier.size(130.dp)
                    ) {
                        // Background glow ring
                        Box(
                            modifier = Modifier
                                .size(110.dp)
                                .border(8.dp, Color(0x11FFFFFF), CircleShape)
                        )
                        // Active colored ring representing confidence percentage
                        Box(
                            modifier = Modifier
                                .size(110.dp)
                                .border(
                                    width = 8.dp,
                                    brush = Brush.sweepGradient(
                                        colors = listOf(
                                            MaterialTheme.colorScheme.primary,
                                            GreenStatus,
                                            MaterialTheme.colorScheme.primary
                                        )
                                    ),
                                    shape = CircleShape
                                )
                        )
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            val confidencePercent = (uiState.vehiclePredictionConfidence * 100).toInt()
                            Text(
                                text = "$confidencePercent%",
                                style = MaterialTheme.typography.headlineLarge,
                                fontWeight = FontWeight.ExtraBold,
                                color = Color.White
                            )
                            Text(
                                text = "Confidence",
                                style = MaterialTheme.typography.labelMedium,
                                color = GreenStatus,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Vehicle State",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        Text(
                            text = uiState.vehiclePredictionLabel.ifEmpty { "Unknown" },
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            }

            // Crimson Action Card: Schedule User
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(18.dp))
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(Color(0x1FEF5350), Color(0x0CEF5350))
                        )
                    )
                    .border(
                        width = 1.dp,
                        color = Color(0x33EF5350),
                        shape = RoundedCornerShape(18.dp)
                    )
                    .clickable { onMaintenanceClick() }
                    .padding(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    // Leading calendar icon with red background low opacity
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(Color(0x26EF5350), shape = RoundedCornerShape(10.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.CalendarToday,
                            contentDescription = "Schedule icon",
                            tint = Color(0xFFEF5350),
                            modifier = Modifier.size(20.dp)
                        )
                    }

                    // Content details
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "Schedule User",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Box(
                                modifier = Modifier
                                    .background(Color(0x26EF5350), shape = RoundedCornerShape(6.dp))
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "Booking Now",
                                    color = Color(0xFFEF5350),
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        Text(
                            text = "Tap to schedule vehicle maintenance",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                    }

                    // Trailing icon
                    Icon(
                        imageVector = Icons.Default.ChevronRight,
                        contentDescription = "Chevron Right",
                        tint = Color(0xFFEF5350),
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            // 3. Local AI Diagnosis Card (Replacing Wheel Status Card)
            val severityColor = when (uiState.localSeverity) {
                "Critical" -> Color(0xFFEF5350)
                "Warning" -> Color(0xFFFFB74D)
                else -> GreenStatus
            }
            val severityBgColor = when (uiState.localSeverity) {
                "Critical" -> Color(0x1FEF5350)
                "Warning" -> Color(0x1FFFB74D)
                else -> Color(0x1F10B981)
            }

            GlassmorphicCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "AI Diagnosis",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Box(
                            modifier = Modifier
                                .background(severityBgColor, shape = RoundedCornerShape(6.dp))
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = uiState.localSeverity,
                                color = severityColor,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(severityBgColor.copy(alpha = 0.1f), shape = RoundedCornerShape(10.dp))
                            .border(1.dp, severityColor.copy(alpha = 0.3f), shape = RoundedCornerShape(10.dp))
                            .padding(12.dp)
                    ) {
                        Column(
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = uiState.localDiagnosis,
                                style = MaterialTheme.typography.bodyLarge,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Text(
                                text = "Recommendation: ${uiState.localRecommendation}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                        }
                    }
                }
            }

            // 4. Prediction Inputs Card
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Prediction Inputs",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )

                GlassmorphicCard(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        // Row 1: Temperature & Battery
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(text = "🌡 Temperature", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                                Text(text = "${uiState.temperature} °C", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = Color.White)
                            }
                            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(text = "🔋 Battery Voltage", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                                Text(text = "${uiState.voltage} V", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = Color.White)
                            }
                        }

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                        // Row 2: GPS Status
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "📍 GPS Status", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                            Box(
                                modifier = Modifier
                                    .background(
                                        if (uiState.gpsConnected) Color(0x1F10B981) else Color(0x1FEF5350),
                                        shape = RoundedCornerShape(6.dp)
                                    )
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = if (uiState.gpsConnected) "Connected" else "Offline",
                                    color = if (uiState.gpsConnected) GreenStatus else Color(0xFFEF5350),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        // Row 3: Gas Sensor Value
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "⛽ Gas Sensor", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                            Text(
                                text = "${uiState.gasSensorValue} ${uiState.gasSensorUnit}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }

                        // Row 4: MPU1 Status
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "📈 MPU1 Status", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                            Box(
                                modifier = Modifier
                                    .background(
                                        if (uiState.mpu1Connected) Color(0x1F10B981) else Color(0x1FEF5350),
                                        shape = RoundedCornerShape(6.dp)
                                    )
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = if (uiState.mpu1Connected) "Active" else "Offline",
                                    color = if (uiState.mpu1Connected) GreenStatus else Color(0xFFEF5350),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        // Row 5: MPU2 Status
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "🌀 MPU2 Status", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                            Box(
                                modifier = Modifier
                                    .background(
                                        if (uiState.mpu2Connected) Color(0x1F10B981) else Color(0x1FEF5350),
                                        shape = RoundedCornerShape(6.dp)
                                    )
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = if (uiState.mpu2Connected) "Active" else "Offline",
                                    color = if (uiState.mpu2Connected) GreenStatus else Color(0xFFEF5350),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                        // Row 5: Last Updated
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "🕒 Last Updated", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                            val displayTime = if (uiState.lastUpdated.length > 10) {
                                uiState.lastUpdated.substring(11, 19)
                            } else {
                                uiState.lastUpdated.ifEmpty { "--:--:--" }
                            }
                            Text(
                                text = displayTime,
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }

                        HorizontalDivider(color = Color(0x1AFFFFFF), thickness = 1.dp)

                        // Footer Explanatory Text
                        Text(
                            text = "Machine Health Score is calculated using the latest sensor readings.",
                            style = MaterialTheme.typography.labelMedium,
                            color = TextSecondary,
                            fontWeight = FontWeight.Normal
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(60.dp)) // Extra space to scroll past the FAB
        }
    }
}

@Composable
fun StatusBadge(text: String) {
    Box(
        modifier = Modifier
            .background(Color(0x1AFFFFFF), shape = RoundedCornerShape(10.dp))
            .border(1.dp, Color(0x13FFFFFF), shape = RoundedCornerShape(10.dp))
            .padding(horizontal = 10.dp, vertical = 6.dp)
    ) {
        Text(
            text = text,
            color = Color.White,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
fun MachineCard(
    machine: Machine,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(Color(0x0CFFFFFF))
            .border(1.dp, Color(0x0FFFFFFF), RoundedCornerShape(14.dp))
            .clickable(onClick = onClick)
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = machine.name,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = machine.type,
                    style = MaterialTheme.typography.labelMedium,
                    color = TextSecondary
                )
            }

            Column(
                horizontalAlignment = Alignment.End,
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "${machine.healthScore}% Health",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = if (machine.healthScore >= 90) GreenStatus else if (machine.healthScore >= 75) Color(0xFFFFB74D) else Color.Red
                )
                Text(
                    text = machine.status,
                    style = MaterialTheme.typography.labelMedium,
                    color = if (machine.status == "Healthy") GreenStatus else Color(0xFFFFB74D)
                )
            }
        }
    }
}
