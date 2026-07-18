# PulseDrive 🚗⚡

> **AI-powered vehicle health monitoring system optimized for Qualcomm Snapdragon NPU**
> Qualcomm Snapdragon Hackathon 2024

---

## Project Overview

PulseDrive is an intelligent, real-time vehicle health monitoring system that:

- 📡 **Ingests** live vehicle sensor data (temperature, current, smoke, vibration, speed)
- 🧠 **Predicts** vehicle health status (NORMAL / WARNING / CRITICAL) using AI inference
- 📊 **Scores** overall vehicle health on a 0–100 scale
- 🗣️ **Explains** predictions in plain language via Sarvam AI (multilingual, Indian languages)
- ⚡ **Runs on-device** using Qualcomm Snapdragon NPU for ultra-low-latency, energy-efficient inference

---

## Architecture

```
Vehicle Sensors
      ↓
FastAPI Backend  (Python 3.11 + Uvicorn)
      ↓
VehicleIntelligenceEngine
  ├─ Predictor → ONNX Runtime / Qualcomm AI Hub
  ├─ Health Score Calculator
  ├─ Risk Classifier
  └─ Sarvam AI GenAI Explanation
      ↓
REST API / WebSocket Response
```

See [`docs/architecture.md`](docs/architecture.md) for the full system design.

---

## Folder Structure

```
PulseDrive/
│
├── backend/                    # FastAPI application
│   ├── app.py                  # Application entry point
│   ├── config.py               # Pydantic settings
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── api/
│   │   ├── routes.py           # REST API endpoints
│   │   └── websocket.py        # WebSocket streaming (future)
│   │
│   ├── core/
│   │   ├── logger.py           # Logging configuration
│   │   ├── constants.py        # Application constants
│   │   └── utils.py            # Helper utilities
│   │
│   ├── inference/
│   │   ├── predictor.py        # Model predictor class
│   │   ├── vehicle_intelligence.py  # Pipeline orchestrator
│   │   ├── health_score.py     # Health score calculator
│   │   └── runtime/
│   │       ├── base_runtime.py    # Abstract runtime interface
│   │       ├── onnx_runtime.py    # ONNX Runtime backend
│   │       └── qualcomm_runtime.py # Snapdragon NPU backend
│   │
│   ├── genai/
│   │   ├── sarvam.py           # Sarvam AI client
│   │   ├── prompts.py          # Prompt templates
│   │   └── explain.py          # Explanation generator
│   │
│   ├── models/
│   │   ├── optimized/          # ONNX / Qualcomm model binaries
│   │   └── labels.json         # Class index → label mapping
│   │
│   ├── data/
│   │   ├── sample.json         # Sample sensor data
│   │   └── live/               # Live sensor data (runtime)
│   │
│   └── qualcomm/
│       ├── deployment.md       # Qualcomm AI Hub deployment guide
│       └── benchmark.md        # Performance benchmark results
│
├── training/                   # ML training pipeline
│   ├── preprocess.py           # Data preprocessing
│   ├── feature_engineering.py  # Feature derivation + normalization
│   ├── train.py                # Model training
│   ├── evaluate.py             # Evaluation metrics
│   └── export_onnx.py          # ONNX model export
│
├── dataset/
│   ├── raw/                    # Raw sensor data
│   ├── processed/              # Processed Parquet splits
│   └── synthetic/              # Synthetic data for augmentation
│
├── docs/
│   ├── architecture.md         # System architecture
│   ├── api.md                  # API reference
│   └── model.md                # Model specification
│
├── README.md
└── .gitignore
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install

```bash
cd backend
pip install -r requirements.txt
```

### Run

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Predict (mock response)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 42,
    "current": 1.4,
    "smoke": 0,
    "vibration": 0.32,
    "speed": 18
  }'
```

**Expected Response:**
```json
{
  "prediction": "NORMAL",
  "confidence": 0.98,
  "health_score": 100,
  "risk": "LOW",
  "summary": "Placeholder prediction. No real inference yet.",
  "recommendation": "No action required. (Mock response)"
}
```

Interactive Swagger docs at: **http://localhost:8000/docs**

---

## Snapdragon AI Flow

```
TensorFlow / PyTorch / sklearn
           ↓
    Export to ONNX
    (training/export_onnx.py)
           ↓
    Validate with onnxruntime
           ↓
    Submit to Qualcomm AI Hub
           ↓
    Compile for Snapdragon HTP
           ↓
     INT8 Quantization
     (4× size, 10× speed)
           ↓
    Download optimized binary
           ↓
    On-device inference via
      QualcommRuntime
```

---

## Tech Stack

| Layer          | Technology                                   |
|----------------|----------------------------------------------|
| API Framework  | FastAPI + Uvicorn                            |
| Validation     | Pydantic v2                                  |
| Inference      | ONNX Runtime → Qualcomm AI Hub               |
| GenAI          | Sarvam AI (multilingual Indian languages)    |
| Edge Target    | Snapdragon 8 Elite (45 TOPS NPU)             |
| Language       | Python 3.11                                  |

---

## Future Roadmap

| Phase | Feature                                          | Status      |
|-------|--------------------------------------------------|-------------|
| 1     | FastAPI boilerplate + mock predictions           | ✅ Done      |
| 2     | Dataset collection + labeling                    | 🔲 Pending  |
| 3     | Model training (XGBoost / MLP)                   | 🔲 Pending  |
| 4     | ONNX export + validation                         | 🔲 Pending  |
| 5     | Qualcomm AI Hub compilation                      | 🔲 Pending  |
| 6     | Sarvam AI multilingual explanation integration   | 🔲 Pending  |
| 7     | WebSocket real-time streaming                    | 🔲 Pending  |
| 8     | Mobile / OBD display integration                 | 🔲 Pending  |

---

## API Reference

See [`docs/api.md`](docs/api.md) for the full API documentation.

---

## License

MIT License — PulseDrive Team
