package com.pulsedrive.inference

import android.content.Context
import android.util.Log
import com.pulsedrive.data.remote.MpuDataDto
import java.nio.ByteBuffer
import java.nio.ByteOrder

class VehicleInference(context: Context) {

    private var liteRTManager: LiteRTManager? = null
    private val inputScale = 0.04041363f
    private val inputZeroPoint = -11
    private val outputScale = 0.00390625f
    private val outputZeroPoint = -128

    private val labels = listOf("Stationary", "Moving", "Inclined", "Declined")

    private val inputBuffer: ByteBuffer = ByteBuffer.allocateDirect(6).apply {
        order(ByteOrder.nativeOrder())
    }
    private val outputBuffer: ByteBuffer = ByteBuffer.allocateDirect(4).apply {
        order(ByteOrder.nativeOrder())
    }

    init {
        try {
            liteRTManager = LiteRTManager(context, "vehicle_state_model_int8.tflite")
            Log.d("VehicleInference", "Vehicle State Model Loaded Successfully")
        } catch (e: Exception) {
            Log.e("VehicleInference", "Failed to load vehicle state model", e)
        }
    }

    fun predict(mpu: MpuDataDto?): PredictionResult {
        if (mpu == null || liteRTManager == null) {
            return PredictionResult(label = "Unknown", confidence = 0f)
        }

        try {
            val accX = mpu.accX.toFloat()
            val accY = mpu.accY.toFloat()
            val accZ = mpu.accZ.toFloat()
            val gyroX = mpu.gyroX.toFloat()
            val gyroY = mpu.gyroY.toFloat()
            val gyroZ = mpu.gyroZ.toFloat()

            // 1. Quantize features
            val qAccX = InferenceUtils.quantize(accX, inputScale, inputZeroPoint)
            val qAccY = InferenceUtils.quantize(accY, inputScale, inputZeroPoint)
            val qAccZ = InferenceUtils.quantize(accZ, inputScale, inputZeroPoint)
            val qGyroX = InferenceUtils.quantize(gyroX, inputScale, inputZeroPoint)
            val qGyroY = InferenceUtils.quantize(gyroY, inputScale, inputZeroPoint)
            val qGyroZ = InferenceUtils.quantize(gyroZ, inputScale, inputZeroPoint)

            // Log raw and quantized inputs
            Log.d("VehicleInference", "Raw Input: accX=$accX, accY=$accY, accZ=$accZ, gyroX=$gyroX, gyroY=$gyroY, gyroZ=$gyroZ")
            Log.d("VehicleInference", "Quantized Input: accX=$qAccX, accY=$qAccY, accZ=$qAccZ, gyroX=$qGyroX, gyroY=$qGyroY, gyroZ=$qGyroZ")

            // 2. Load into ByteBuffer
            inputBuffer.rewind()
            inputBuffer.put(qAccX)
            inputBuffer.put(qAccY)
            inputBuffer.put(qAccZ)
            inputBuffer.put(qGyroX)
            inputBuffer.put(qGyroY)
            inputBuffer.put(qGyroZ)

            // 3. Run Inference
            inputBuffer.rewind()
            outputBuffer.rewind()
            liteRTManager?.run(inputBuffer, outputBuffer)

            // 4. Read output bytes
            outputBuffer.rewind()
            val rawOutput = ByteArray(4)
            outputBuffer.get(rawOutput)

            Log.d("VehicleInference", "Raw Output Bytes: ${rawOutput.contentToString()}")

            // 5. Dequantize outputs and find highest probability class
            val dequantizedProbabilities = FloatArray(4) { i ->
                InferenceUtils.dequantize(rawOutput[i], outputScale, outputZeroPoint)
            }

            Log.d("VehicleInference", "Dequantized Probabilities: ${dequantizedProbabilities.contentToString()}")

            var maxIndex = 0
            var maxProb = dequantizedProbabilities[0]
            for (i in 1 until dequantizedProbabilities.size) {
                if (dequantizedProbabilities[i] > maxProb) {
                    maxProb = dequantizedProbabilities[i]
                    maxIndex = i
                }
            }

            val finalLabel = labels.getOrElse(maxIndex) { "Unknown" }
            Log.d("VehicleInference", "Final Label: $finalLabel, Confidence: $maxProb")

            return PredictionResult(label = finalLabel, confidence = maxProb)

        } catch (e: Exception) {
            Log.e("VehicleInference", "Error during vehicle state prediction", e)
            return PredictionResult(label = "Unknown", confidence = 0f)
        }
    }

    fun close() {
        liteRTManager?.close()
    }
}
