package com.pulsedrive.inference

import android.content.Context
import android.util.Log
import com.pulsedrive.data.remote.MpuDataDto
import java.nio.ByteBuffer
import java.nio.ByteOrder

class WheelInference(context: Context) {

    private var liteRTManager: LiteRTManager? = null
    private val inputScale = 0.05509732f
    private val inputZeroPoint = -17
    private val outputScale = 0.00390625f
    private val outputZeroPoint = -128

    private val labels = listOf("Balanced", "Imbalance")

    private val inputBuffer: ByteBuffer = ByteBuffer.allocateDirect(3).apply {
        order(ByteOrder.nativeOrder())
    }
    private val outputBuffer: ByteBuffer = ByteBuffer.allocateDirect(2).apply {
        order(ByteOrder.nativeOrder())
    }

    init {
        try {
            liteRTManager = LiteRTManager(context, "wheel_imbalance_model_int8.tflite")
            Log.d("WheelInference", "Wheel Imbalance Model Loaded Successfully")
        } catch (e: Exception) {
            Log.e("WheelInference", "Failed to load wheel imbalance model", e)
        }
    }

    fun predict(mpu: MpuDataDto?): PredictionResult {
        if (mpu == null || liteRTManager == null) {
            return PredictionResult(label = "Unknown", confidence = 0f)
        }

        try {
            val gyroX = mpu.gyroX.toFloat()
            val gyroY = mpu.gyroY.toFloat()
            val gyroZ = mpu.gyroZ.toFloat()

            // 1. Quantize features
            val qGyroX = InferenceUtils.quantize(gyroX, inputScale, inputZeroPoint)
            val qGyroY = InferenceUtils.quantize(gyroY, inputScale, inputZeroPoint)
            val qGyroZ = InferenceUtils.quantize(gyroZ, inputScale, inputZeroPoint)

            // Log raw and quantized inputs
            Log.d("WheelInference", "Raw Input: gyroX=$gyroX, gyroY=$gyroY, gyroZ=$gyroZ")
            Log.d("WheelInference", "Quantized Input: gyroX=$qGyroX, gyroY=$qGyroY, gyroZ=$qGyroZ")

            // 2. Load into ByteBuffer
            inputBuffer.rewind()
            inputBuffer.put(qGyroX)
            inputBuffer.put(qGyroY)
            inputBuffer.put(qGyroZ)

            // 3. Run Inference
            inputBuffer.rewind()
            outputBuffer.rewind()
            liteRTManager?.run(inputBuffer, outputBuffer)

            // 4. Read output bytes
            outputBuffer.rewind()
            val rawOutput = ByteArray(2)
            outputBuffer.get(rawOutput)

            Log.d("WheelInference", "Raw Output Bytes: ${rawOutput.contentToString()}")

            // 5. Dequantize outputs and find highest probability class
            val dequantizedProbabilities = FloatArray(2) { i ->
                InferenceUtils.dequantize(rawOutput[i], outputScale, outputZeroPoint)
            }

            Log.d("WheelInference", "Dequantized Probabilities: ${dequantizedProbabilities.contentToString()}")

            var maxIndex = 0
            var maxProb = dequantizedProbabilities[0]
            for (i in 1 until dequantizedProbabilities.size) {
                if (dequantizedProbabilities[i] > maxProb) {
                    maxProb = dequantizedProbabilities[i]
                    maxIndex = i
                }
            }

            val finalLabel = labels.getOrElse(maxIndex) { "Unknown" }
            Log.d("WheelInference", "Final Label: $finalLabel, Confidence: $maxProb")

            return PredictionResult(label = finalLabel, confidence = maxProb)

        } catch (e: Exception) {
            Log.e("WheelInference", "Error during wheel imbalance prediction", e)
            return PredictionResult(label = "Unknown", confidence = 0f)
        }
    }

    fun close() {
        liteRTManager?.close()
    }
}
