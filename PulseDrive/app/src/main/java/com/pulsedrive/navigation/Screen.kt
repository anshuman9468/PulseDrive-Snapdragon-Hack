package com.pulsedrive.navigation

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Register : Screen("register")
    object Dashboard : Screen("dashboard")
    object Monitor : Screen("monitor")
    object AI : Screen("ai")
    object Maintenance : Screen("maintenance")
    object Notifications : Screen("notifications")
    object Profile : Screen("profile")
    object Reports : Screen("reports")
    object Map : Screen("map")
    object MachineDetail : Screen("machine_detail/{machineId}") {
        fun createRoute(machineId: String) = "machine_detail/$machineId"
    }
}
