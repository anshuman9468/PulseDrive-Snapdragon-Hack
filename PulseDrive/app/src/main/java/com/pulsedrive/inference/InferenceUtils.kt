package com.pulsedrive.inference

import kotlin.math.roundToInt

object InferenceUtils {

    /**
     * Quantizes a Float value to INT8 (Byte) representation.
     * Formula: q = clamp(round(value / scale) + zeroPoint, -128, 127)
     */
    fun quantize(value: Float, scale: Float, zeroPoint: Int): Byte {
        val q = (value / scale).roundToInt() + zeroPoint
        return q.coerceIn(-128, 127).toByte()
    }

    /**
     * Dequantizes an INT8 (Byte) value back to its Float representation.
     * Formula: r = (q - zeroPoint) * scale
     */
    fun dequantize(value: Byte, scale: Float, zeroPoint: Int): Float {
        return (value.toInt() - zeroPoint) * scale
    }

    /**
     * Helper to quantize an entire list or array of Float values.
     */
    fun quantizeList(values: List<Float>, scale: Float, zeroPoint: Int): ByteArray {
        return ByteArray(values.size) { i ->
            quantize(values[i], scale, zeroPoint)
        }
    }

    /**
     * Helper to dequantize an entire ByteArray back to a List of Float values.
     */
    fun dequantizeList(values: ByteArray, scale: Float, zeroPoint: Int): List<Float> {
        return values.map { dequantize(it, scale, zeroPoint) }
    }
}
