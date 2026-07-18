# PulseDrive — System Architecture

## Overview

PulseDrive is an AI-powered vehicle health monitoring system designed for
Qualcomm Snapdragon-powered edge devices. It analyzes real-time sensor data
and produces instant health predictions, risk classifications, and multilingual
GenAI explanations via Sarvam AI.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IoT / Edge Device                        │
│                  (Snapdragon SoC)                           │
│                                                             │
│  Vehicle Sensors  →  Sensor HAL  →  PulseDrive Backend     │
│  (Temp, Current,                                            │
│   Smoke, Vibration,                                         │
│   Speed)                                                    │
└────────────────────────────┬────────────────────────────────┘
                             │ REST / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  PulseDrive Backend (FastAPI)                │
│                                                             │
│  POST /api/predict                                          │
│       ↓                                                     │
│  VehicleIntelligenceEngine                                  │
│       ├─ Predictor → [ONNXRuntime | QualcommRuntime]        │
│       ├─ HealthScoreCalculator                              │
│       ├─ RiskClassifier                                     │
│       └─ GenAI Explainer (Sarvam AI)                        │
│                                                             │
│  WebSocket /ws/stream (real-time streaming — future)        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Client / Dashboard                      │
│           (Mobile App / Web Dashboard / OBD Display)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### `backend/api/`
- **routes.py** — REST API endpoints (`/health`, `/predict`)
- **websocket.py** — WebSocket real-time streaming endpoint

### `backend/core/`
- **logger.py** — Structured logging factory
- **constants.py** — Application-wide constants
- **utils.py** — Pure utility functions

### `backend/inference/`
- **vehicle_intelligence.py** — Orchestrates the full inference pipeline
- **predictor.py** — Runtime-agnostic model predictor
- **health_score.py** — Weighted health score calculator
- **runtime/base_runtime.py** — Abstract runtime interface
- **runtime/onnx_runtime.py** — CPU/GPU ONNX Runtime backend
- **runtime/qualcomm_runtime.py** — Snapdragon NPU backend (Qualcomm AI Hub)

### `backend/genai/`
- **sarvam.py** — Sarvam AI API client
- **prompts.py** — Prompt templates for explanation generation
- **explain.py** — Explanation orchestrator function

### `training/`
- **preprocess.py** — Data cleaning and splitting
- **feature_engineering.py** — Feature derivation and normalization
- **train.py** — Model training pipeline
- **evaluate.py** — Evaluation metrics and reports
- **export_onnx.py** — ONNX model export and validation

---

## Inference Pipeline

```
SensorData (Pydantic)
       ↓
Validation + Normalization
       ↓
Feature Vector  (1 × 5 float32)
       ↓
Runtime.predict()
  ├─ ONNXRuntime (dev/CPU)
  └─ QualcommRuntime (prod/NPU)
       ↓
Raw Logits  (1 × 3)
       ↓
Softmax → Probabilities
       ↓
Argmax → Prediction Label
       ↓
HealthScore Calculation
       ↓
Risk Classification
       ↓
Sarvam AI Explanation
       ↓
PredictionResponse (JSON)
```

---

## Snapdragon AI Deployment Flow

```
TensorFlow / PyTorch / sklearn
       ↓
Export to ONNX  (training/export_onnx.py)
       ↓
Validate with onnxruntime
       ↓
Submit to Qualcomm AI Hub
       ↓
Compile for Snapdragon HTP
       ↓
INT8 Quantization (4× size reduction)
       ↓
Download optimized binary
       ↓
On-device inference via QualcommRuntime
```
