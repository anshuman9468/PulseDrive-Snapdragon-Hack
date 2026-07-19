package com.pulsedrive.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.pulsedrive.ui.components.GlassmorphicCard
import com.pulsedrive.ui.theme.GreenStatus
import com.pulsedrive.ui.theme.NearBlack
import com.pulsedrive.ui.theme.TextSecondary
import com.pulsedrive.viewmodel.MonitorViewModel

@Composable
fun MonitorScreen(
    viewModel: MonitorViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    // Pulsing animation for the Live Indicator dot
    val infiniteTransition = rememberInfiniteTransition(label = "live_pulse")
    val alphaAnim by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(NearBlack)
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // Title Section
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Telemetry Monitor",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = "Real-time edge device sensor streaming",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            }
            // Live Status Indicator
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier
                    .background(Color(0x1F10B981), RoundedCornerShape(20.dp))
                    .padding(horizontal = 10.dp, vertical = 5.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(GreenStatus.copy(alpha = alphaAnim))
                )
                Text(
                    text = "LIVE",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = GreenStatus
                )
            }
        }

        // 1. Connection Status Row (ESP32, WebSocket and Last Updated)
        GlassmorphicCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Connectivity & Sync",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // ESP32 Status badge
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .background(
                                if (uiState.connectionState.esp32) Color(0x1F10B981) else Color(0x1FEF5350),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .border(
                                1.dp,
                                if (uiState.connectionState.esp32) Color(0x3310B981) else Color(0x33EF5350),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .padding(vertical = 8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = if (uiState.connectionState.esp32) "ESP32: Connected" else "ESP32: Offline",
                            color = if (uiState.connectionState.esp32) GreenStatus else Color(0xFFEF5350),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    // Backend Status badge
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .background(
                                if (uiState.connectionState.backend) Color(0x1F10B981) else Color(0x1FEF5350),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .border(
                                1.dp,
                                if (uiState.connectionState.backend) Color(0x3310B981) else Color(0x33EF5350),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .padding(vertical = 8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = if (uiState.connectionState.backend) "Backend: Online" else "Backend: Offline",
                            color = if (uiState.connectionState.backend) GreenStatus else Color(0xFFEF5350),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    // API Status badge
                    Box(
                        modifier = Modifier
                            .weight(1.1f)
                            .background(
                                if (uiState.connectionState.websocket) Color(0x1F10B981) else Color(0x1F3B82F6),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .border(
                                1.dp,
                                if (uiState.connectionState.websocket) Color(0x3310B981) else Color(0x333B82F6),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .padding(vertical = 8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = if (uiState.connectionState.websocket) "API: WS Stream" else "API: HTTP Poll",
                            color = if (uiState.connectionState.websocket) GreenStatus else MaterialTheme.colorScheme.primary,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Last Updated",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary
                    )
                    Text(
                        text = uiState.timestamp.ifEmpty { "Waiting..." },
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }
        }

        // 2. Live Sensor Cards (Temperature & Battery Voltage)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            SensorValueCard(
                label = "🌡 Temperature",
                value = "${uiState.temperature} °C",
                modifier = Modifier.weight(1f)
            )
            SensorValueCard(
                label = "🔋 Battery",
                value = "${uiState.voltage} V",
                modifier = Modifier.weight(1f)
            )
        }

        // 3. Gas Sensor Card
        GlassmorphicCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "⛽ Gas Sensor",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = "${uiState.gasSensorValue} ${uiState.gasSensorUnit}",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }

        // 4. MPU1 Accelerometer & Gyroscope Cards
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // MPU1 Accelerometer Card
            GlassmorphicCard(
                modifier = Modifier.weight(1f)
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "📈 MPU1 Accel (g)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(text = "X: ${String.format("%.3f", uiState.mpu1AccX)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Y: ${String.format("%.3f", uiState.mpu1AccY)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Z: ${String.format("%.3f", uiState.mpu1AccZ)}", fontSize = 12.sp, color = Color.White)
                    }
                }
            }

            // MPU1 Gyroscope Card
            GlassmorphicCard(
                modifier = Modifier.weight(1f)
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "🌀 MPU1 Gyro (rad/s)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(text = "X: ${String.format("%.3f", uiState.mpu1GyroX)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Y: ${String.format("%.3f", uiState.mpu1GyroY)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Z: ${String.format("%.3f", uiState.mpu1GyroZ)}", fontSize = 12.sp, color = Color.White)
                    }
                }
            }
        }

        // 5. MPU2 Accelerometer & Gyroscope Cards
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // MPU2 Accelerometer Card
            GlassmorphicCard(
                modifier = Modifier.weight(1f)
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "📈 MPU2 Accel (g)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(text = "X: ${String.format("%.3f", uiState.mpu2AccX)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Y: ${String.format("%.3f", uiState.mpu2AccY)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Z: ${String.format("%.3f", uiState.mpu2AccZ)}", fontSize = 12.sp, color = Color.White)
                    }
                }
            }

            // MPU2 Gyroscope Card
            GlassmorphicCard(
                modifier = Modifier.weight(1f)
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "🌀 MPU2 Gyro (rad/s)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(text = "X: ${String.format("%.3f", uiState.mpu2GyroX)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Y: ${String.format("%.3f", uiState.mpu2GyroY)}", fontSize = 12.sp, color = Color.White)
                        Text(text = "Z: ${String.format("%.3f", uiState.mpu2GyroZ)}", fontSize = 12.sp, color = Color.White)
                    }
                }
            }
        }

        // 5. GPS Card (Latitude & Longitude)
        GlassmorphicCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(10.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "GPS Coordinates",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Latitude", style = MaterialTheme.typography.labelMedium, color = TextSecondary)
                        Text(text = String.format("%.6f", uiState.gpsLat), style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = Color.White)
                    }
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Longitude", style = MaterialTheme.typography.labelMedium, color = TextSecondary)
                        Text(text = String.format("%.6f", uiState.gpsLng), style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = Color.White)
                    }
                }
            }
        }

        // 6. Vibration Graph (Future Graph Placeholder / accZ wave representation)
        GlassmorphicCard(
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp)
        ) {
            val primaryColor = MaterialTheme.colorScheme.primary
            val dataPoints = uiState.signalDataPoints

            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Vibration Wave Analysis (accZ)",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )

                if (dataPoints.isNotEmpty()) {
                    Canvas(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f)
                            .padding(vertical = 8.dp)
                    ) {
                        val width = size.width
                        val height = size.height
                        val maxPoints = dataPoints.size
                        val stepX = width / (maxPoints - 1)

                        // Draw Grid Lines (horizontal)
                        val gridLines = 4
                        for (i in 0..gridLines) {
                            val y = height * (i.toFloat() / gridLines)
                            drawLine(
                                color = Color(0x0CFFFFFF),
                                start = Offset(0f, y),
                                end = Offset(width, y),
                                strokeWidth = 1.dp.toPx()
                            )
                        }

                        // Create Path for Line
                        val path = Path().apply {
                            val startX = 0f
                            // MPU6050 accZ is centered around 9.8g (gravity) or fluctuating
                            // We scale it dynamically to fit the Canvas height
                            val startY = height - ((dataPoints[0].coerceIn(5f, 15f) - 5f) / 10f * height)
                            moveTo(startX, startY)

                            for (i in 1 until maxPoints) {
                                val nextX = i * stepX
                                val nextY = height - ((dataPoints[i].coerceIn(5f, 15f) - 5f) / 10f * height)
                                lineTo(nextX, nextY)
                            }
                        }

                        // Create Filled Path (Area below the line)
                        val filledPath = Path().apply {
                            addPath(path)
                            lineTo(width, height)
                            lineTo(0f, height)
                            close()
                        }

                        // Draw Filled Area
                        drawPath(
                            path = filledPath,
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    primaryColor.copy(alpha = 0.25f),
                                    Color.Transparent
                                )
                            )
                        )

                        // Draw Graph Line
                        drawPath(
                            path = path,
                            color = primaryColor,
                            style = Stroke(width = 3.dp.toPx())
                        )

                        // Draw Outer glowing path line
                        drawPath(
                            path = path,
                            color = primaryColor.copy(alpha = 0.4f),
                            style = Stroke(width = 6.dp.toPx())
                        )
                    }
                } else {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(text = "Awaiting Live Telemetry Streams...", color = TextSecondary, fontSize = 12.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun SensorValueCard(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(Color(0x0CFFFFFF))
            .border(1.dp, Color(0x0FFFFFFF), RoundedCornerShape(12.dp))
            .padding(14.dp)
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }
    }
}

@Composable
fun AxisValueItem(
    axis: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0x06FFFFFF))
            .border(1.dp, Color(0x0AFFFFFF), RoundedCornerShape(8.dp))
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            Text(
                text = axis,
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = value,
                fontSize = 13.sp,
                color = Color.White,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}
