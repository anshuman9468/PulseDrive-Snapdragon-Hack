package com.pulsedrive.inference

import android.content.Context
import com.pulsedrive.data.remote.DashboardResponse
import com.pulsedrive.data.remote.MpuDataDto

class PredictionManager private constructor(context: Context) {

    private val vehicleInference = VehicleInference(context)
    private val wheelInference = WheelInference(context)

    fun predictVehicle(mpu2: MpuDataDto?): PredictionResult {
        return vehicleInference.predict(mpu2)
    }

    fun predictWheel(mpu1: MpuDataDto?): PredictionResult {
        return wheelInference.predict(mpu1)
    }

    fun predictAll(response: DashboardResponse): PredictionBundle {
        val mpu1 = response.data.mpu1
        val mpu2 = response.data.mpu2
        return PredictionBundle(
            vehiclePrediction = predictVehicle(mpu2),
            wheelPrediction = predictWheel(mpu1)
        )
    }

    fun close() {
        vehicleInference.close()
        wheelInference.close()
    }

    companion object {
        @Volatile
        private var instance: PredictionManager? = null

        fun initialize(context: Context) {
            if (instance == null) {
                synchronized(this) {
                    if (instance == null) {
                        instance = PredictionManager(context.applicationContext)
                    }
                }
            }
        }

        fun getInstance(): PredictionManager {
            return instance ?: throw IllegalStateException("PredictionManager has not been initialized.")
        }
    }
}
