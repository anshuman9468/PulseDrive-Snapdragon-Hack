package com.pulsedrive.inference

import android.content.Context
import android.content.res.AssetFileDescriptor
import android.util.Log
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.DataType
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class LiteRTManager(
    context: Context,
    modelFileName: String
) {

    private val interpreter: Interpreter

    init {
        interpreter = Interpreter(loadModelFile(context, modelFileName))
    }

    private fun loadModelFile(
        context: Context,
        modelFileName: String
    ): MappedByteBuffer {

        val fileDescriptor: AssetFileDescriptor =
            context.assets.openFd(modelFileName)

        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)

        val fileChannel = inputStream.channel

        return fileChannel.map(
            FileChannel.MapMode.READ_ONLY,
            fileDescriptor.startOffset,
            fileDescriptor.declaredLength
        )
    }

    fun printModelInfo() {

        val inputTensor = interpreter.getInputTensor(0)
        val outputTensor = interpreter.getOutputTensor(0)

        Log.d("LiteRT", "==========================")
        Log.d("LiteRT", "Input Shape  : ${inputTensor.shape().contentToString()}")
        Log.d("LiteRT", "Input Type   : ${inputTensor.dataType()}")
        Log.d("LiteRT", "Output Shape : ${outputTensor.shape().contentToString()}")
        Log.d("LiteRT", "Output Type  : ${outputTensor.dataType()}")

        val inputQuant = inputTensor.quantizationParams()
        val outputQuant = outputTensor.quantizationParams()

        Log.d("LiteRT", "Input Scale      : ${inputQuant.scale}")
        Log.d("LiteRT", "Input ZeroPoint  : ${inputQuant.zeroPoint}")

        Log.d("LiteRT", "Output Scale     : ${outputQuant.scale}")
        Log.d("LiteRT", "Output ZeroPoint : ${outputQuant.zeroPoint}")

        Log.d("LiteRT", "==========================")
    }

    fun run(input: ByteBuffer, output: ByteBuffer) {
        interpreter.run(input, output)
    }

    fun getInputScale(): Float = interpreter.getInputTensor(0).quantizationParams().scale
    fun getInputZeroPoint(): Int = interpreter.getInputTensor(0).quantizationParams().zeroPoint
    fun getOutputScale(): Float = interpreter.getOutputTensor(0).quantizationParams().scale
    fun getOutputZeroPoint(): Int = interpreter.getOutputTensor(0).quantizationParams().zeroPoint
    fun getInputShape(): IntArray = interpreter.getInputTensor(0).shape()
    fun getOutputShape(): IntArray = interpreter.getOutputTensor(0).shape()
    fun getInputType(): DataType = interpreter.getInputTensor(0).dataType()
    fun getOutputType(): DataType = interpreter.getOutputTensor(0).dataType()

    fun close() {
        interpreter.close()
    }
}