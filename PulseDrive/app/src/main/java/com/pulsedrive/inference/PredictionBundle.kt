package com.pulsedrive.inference

data class PredictionBundle(
    val vehiclePrediction: PredictionResult,
    val wheelPrediction: PredictionResult
)
