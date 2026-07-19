package com.pulsedrive

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.pulsedrive.inference.LiteRTManager
import com.pulsedrive.navigation.MainNavGraph
import com.pulsedrive.navigation.Screen
import com.pulsedrive.ui.theme.PulseDriveTheme
import com.pulsedrive.utils.SessionManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize PredictionManager
        try {
            com.pulsedrive.inference.PredictionManager.initialize(this)
            Log.d("MainActivity", "PredictionManager initialized successfully")
        } catch (e: Exception) {
            Log.e("MainActivity", "Failed to initialize PredictionManager", e)
        }

        enableEdgeToEdge()

        val startRoute = if (sessionManager.hasToken()) {
            Screen.Dashboard.route
        } else {
            Screen.Login.route
        }

        setContent {

            PulseDriveTheme {

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {

                    val navController = rememberNavController()

                    MainNavGraph(
                        navController = navController,
                        startDestination = startRoute,
                        sessionManager = sessionManager
                    )
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            com.pulsedrive.inference.PredictionManager.getInstance().close()
            Log.d("MainActivity", "PredictionManager closed successfully")
        } catch (e: Exception) {
            Log.e("MainActivity", "Failed to close PredictionManager", e)
        }
    }
}