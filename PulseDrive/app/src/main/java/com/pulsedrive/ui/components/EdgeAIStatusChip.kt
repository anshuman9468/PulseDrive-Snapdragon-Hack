package com.pulsedrive.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pulsedrive.ui.theme.GreenStatus

@Composable
fun EdgeAIStatusChip(
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .background(Color(0x1F10B981), shape = RoundedCornerShape(12.dp))
            .border(1.dp, Color(0x3310B981), shape = RoundedCornerShape(12.dp))
            .padding(horizontal = 10.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            modifier = Modifier
                .size(6.dp)
                .background(GreenStatus, shape = CircleShape)
        ) {}
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = "Edge AI Active",
            color = GreenStatus,
            fontSize = 11.sp,
            letterSpacing = 0.5.sp
        )
    }
}
