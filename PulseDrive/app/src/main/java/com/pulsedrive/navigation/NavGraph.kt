package com.pulsedrive.navigation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import com.pulsedrive.ui.components.EdgeAIStatusChip
import com.pulsedrive.ui.screens.*
import com.pulsedrive.utils.SessionManager

enum class BottomNavItem(val route: String, val title: String, val icon: ImageVector) {
    DASHBOARD(Screen.Dashboard.route, "Dashboard", Icons.Default.Home),
    MONITOR(Screen.Monitor.route, "Monitor", Icons.Default.Settings),
    AI(Screen.AI.route, "AI", Icons.Default.Star),
    MAINTENANCE(Screen.Maintenance.route, "Maintenance", Icons.Default.Build),
    NOTIFICATIONS(Screen.Notifications.route, "Notifications", Icons.Default.Notifications)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainNavGraph(
    navController: NavHostController,
    startDestination: String,
    sessionManager: SessionManager,
    modifier: Modifier = Modifier
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // Check if the current destination is a bottom nav destination
    val isBottomNavScreen = BottomNavItem.values().any { it.route == currentRoute }
    val isLoginScreen = currentRoute == Screen.Login.route
    val isRegisterScreen = currentRoute == Screen.Register.route

    // 1. Session Expiration Listener
    LaunchedEffect(sessionManager) {
        sessionManager.sessionEvents.collect { event ->
            if (event == SessionManager.SessionEvent.TOKEN_EXPIRED) {
                navController.navigate(Screen.Login.route) {
                    popUpTo(0) { inclusive = true }
                }
            }
        }
    }

    // 2. Route Navigation Protection
    LaunchedEffect(currentRoute) {
        if (currentRoute != null &&
            currentRoute != Screen.Login.route &&
            currentRoute != Screen.Register.route &&
            !sessionManager.hasToken()
        ) {
            navController.navigate(Screen.Login.route) {
                popUpTo(0) { inclusive = true }
            }
        }
    }

    Scaffold(
        topBar = {
            if (!isLoginScreen && !isRegisterScreen) {
                CenterAlignedTopAppBar(
                    title = {
                        Text(
                            text = if (currentRoute == Screen.Map.route) "Vehicle Locator" else "PulseDrive",
                            style = MaterialTheme.typography.titleLarge
                        )
                    },
                    navigationIcon = {
                        if (!isBottomNavScreen) {
                            IconButton(onClick = { navController.popBackStack() }) {
                                Icon(
                                    imageVector = Icons.Default.ArrowBack,
                                    contentDescription = "Back"
                                )
                            }
                        }
                    },
                    actions = {
                        EdgeAIStatusChip(modifier = Modifier.padding(end = 8.dp))
                        if (isBottomNavScreen) {
                            IconButton(onClick = { navController.navigate(Screen.Map.route) }) {
                                Icon(
                                    imageVector = Icons.Default.Map,
                                    contentDescription = "Map"
                                )
                            }
                            IconButton(onClick = { navController.navigate(Screen.Profile.route) }) {
                                Icon(
                                    imageVector = Icons.Default.AccountCircle,
                                    contentDescription = "Profile"
                                )
                            }
                        }
                    },
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = MaterialTheme.colorScheme.background
                    )
                )
            }
        },
        bottomBar = {
            if (isBottomNavScreen) {
                NavigationBar(
                    containerColor = MaterialTheme.colorScheme.surface,
                    tonalElevation = 8.dp
                ) {
                    BottomNavItem.values().forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = {
                                Icon(
                                    imageVector = item.icon,
                                    contentDescription = item.title
                                )
                            },
                            alwaysShowLabel = false
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = modifier.padding(innerPadding)
        ) {
            composable(Screen.Login.route) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Screen.Dashboard.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = {
                        navController.navigate(Screen.Register.route)
                    }
                )
            }
            composable(Screen.Register.route) {
                RegisterScreen(
                    onNavigateBackToLogin = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(Screen.Register.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.Dashboard.route) {
                DashboardScreen(
                    onMachineClick = { machineId ->
                        navController.navigate(Screen.MachineDetail.createRoute(machineId))
                    },
                    onMaintenanceClick = {
                        navController.navigate(Screen.Maintenance.route) {
                            popUpTo(navController.graph.findStartDestination().id) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
            }
            composable(Screen.MachineDetail.route) { backStackEntry ->
                val machineId = backStackEntry.arguments?.getString("machineId")
                MachineDetailScreen(machineId = machineId)
            }
            composable(Screen.Monitor.route) {
                MonitorScreen()
            }
            composable(Screen.AI.route) {
                AiAssistantScreen()
            }
            composable(Screen.Maintenance.route) {
                MaintenanceScreen()
            }
            composable(Screen.Notifications.route) {
                NotificationsScreen()
            }
            composable(Screen.Profile.route) {
                ProfileScreen(
                    onNavigateToReports = {
                        navController.navigate(Screen.Reports.route)
                    },
                    onLogout = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(0) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.Reports.route) {
                ReportsScreen()
            }
            composable(Screen.Map.route) {
                VehicleMapScreen()
            }
        }
    }
}
