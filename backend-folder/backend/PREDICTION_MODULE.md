# Prediction Module Documentation

## Overview

The Prediction module is a production-ready vehicle health prediction system for the PulseDrive API. It follows clean architecture principles with clear separation between API, Service, and Model layers.

## Architecture

```
API Layer (api/prediction.py)
    ↓
Service Layer (services/prediction_service.py)
    ↓
Model Layer (joblib model or mock)
```

### File Structure

```
backend/app/
├── models/
│   └── prediction.py              # Pydantic request/response models
├── services/
│   └── prediction_service.py       # Business logic & prediction engine
├── api/
│   └── prediction.py               # API endpoints & routing
└── main.py                         # Router registration
```

## Components

### 1. Models (`models/prediction.py`)

**PredictionRequest**
- `vehicleId`: Unique vehicle identifier (required)
- `features`: Optional dict with sensor data (rpm, temperature, mileage, etc.)
- `timestamp`: Request timestamp (auto-generated if not provided)

**PredictionResponse**
- `vehicleId`: Vehicle identifier (echo)
- `healthScore`: 0-100 numeric health score
- `status`: One of "healthy", "warning", "critical"
- `confidence`: 0-1 model confidence score
- `recommendation`: Actionable recommendation string
- `timestamp`: Prediction timestamp

**PredictionError**
- `error`: Error message
- `details`: Optional detailed error information
- `timestamp`: Error timestamp

### 2. Service (`services/prediction_service.py`)

The `PredictionService` class handles all prediction logic:

#### Initialization

**With Mock Predictions (Default)**
```python
service = PredictionService()
# Returns realistic mock data based on vehicle ID
```

**With Real ML Model**
```python
service = PredictionService(model_path="path/to/model.pkl")
# Loads joblib model and uses it for predictions
# Falls back to mock if model loading fails
```

#### Key Methods

- `predict(request)` - Main prediction method, routes to mock or model
- `_mock_predict()` - Generates deterministic mock predictions
- `_model_predict()` - Uses loaded joblib model for predictions
- `_prepare_features()` - Prepares features for model input
- `_score_to_status()` - Converts score to status label
- `_generate_recommendation()` - Generates user-friendly recommendations

#### Mock Prediction Logic

Mock predictions are **deterministic** based on `vehicleId`:
- Vehicle IDs with hash < 30: Healthy (score 85-99)
- Vehicle IDs with hash 30-70: Warning (score 60-84)
- Vehicle IDs with hash > 70: Critical (score 20-59)

This ensures consistent results for testing and development.

### 3. API (`api/prediction.py`)

#### Endpoints

**POST /api/predict**
Generate a vehicle health prediction.

Request:
```json
{
  "vehicleId": "VH123456",
  "features": {
    "rpm": 3000,
    "temperature": 85,
    "mileage": 45000,
    "fuel_consumption": 8.5,
    "battery_voltage": 13.5
  }
}
```

Response:
```json
{
  "vehicleId": "VH123456",
  "healthScore": 85.5,
  "status": "healthy",
  "confidence": 0.92,
  "recommendation": "Continue regular maintenance schedule",
  "timestamp": "2026-07-17T21:16:32.856000"
}
```

**GET /api/predict/health**
Check prediction service status.

Response:
```json
{
  "status": "healthy",
  "model_loaded": false,
  "using_mock": true
}
```

## Transitioning to Real ML Models

### Step 1: Prepare Your Model

Train and serialize your model using joblib:

```python
import joblib
from sklearn.ensemble import RandomForestRegressor

# Your trained model
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Save as .pkl or .joblib
joblib.dump(model, "models/vehicle_health_model.pkl")
```

### Step 2: Verify Input/Output Format

Ensure your model expects:
- **Input**: List of features `[rpm, temperature, mileage, fuel_consumption, battery_voltage]`
- **Output**: Health score 0-100

### Step 3: Adapt `_model_predict()` and `_prepare_features()`

Update `prediction_service.py` if your model has different requirements:

```python
@staticmethod
def _prepare_features(features: Optional[Dict[str, Any]]) -> list:
    """Adapt to your model's feature requirements"""
    return [
        features.get("your_feature_1", 0),
        features.get("your_feature_2", 0),
        # ... more features
    ]

def _model_predict(self, request: PredictionRequest) -> PredictionResponse:
    """Adapt model inference to your specific model output"""
    features = self._prepare_features(request.features)
    
    # Your model-specific prediction logic
    health_score = self.model.predict([features])[0]
    confidence = self.model.predict_proba([features])[0].max()
    
    # Rest remains the same...
```

### Step 4: Initialize with Model Path

Update where `PredictionService` is instantiated in `api/prediction.py`:

```python
# Load model from file path
prediction_service = PredictionService(model_path="app/models/vehicle_health_model.pkl")
```

Or use environment variables:

```python
import os
model_path = os.getenv("PREDICTION_MODEL_PATH")
prediction_service = PredictionService(model_path=model_path) if model_path else PredictionService()
```

## Error Handling

The service includes robust error handling:

1. **Model Loading**: Automatically falls back to mock if model fails to load
2. **Prediction Errors**: Catches model prediction errors and falls back to mock
3. **Invalid Input**: Validates vehicleId and features in API layer
4. **Graceful Degradation**: Service always returns valid predictions

## Testing

### Test with Mock Predictions

```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicleId": "VH001",
    "features": {
      "rpm": 3000,
      "temperature": 85
    }
  }'
```

### Test Service Health

```bash
curl "http://localhost:8000/api/predict/health"
```

### Unit Test Example

```python
from app.services.prediction_service import PredictionService
from app.models.prediction import PredictionRequest
from datetime import datetime

service = PredictionService()
request = PredictionRequest(
    vehicleId="TEST_VH001",
    features={"rpm": 3000, "temperature": 85}
)

response = service.predict(request)

assert response.vehicleId == "TEST_VH001"
assert 0 <= response.healthScore <= 100
assert response.status in ["healthy", "warning", "critical"]
assert 0 <= response.confidence <= 1
assert response.recommendation is not None
```

## Production Deployment

### Environment Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install joblib  # For model loading
   ```

2. **Place Model File**
   ```bash
   cp vehicle_health_model.pkl backend/app/models/
   ```

3. **Set Model Path (Optional)**
   ```bash
   export PREDICTION_MODEL_PATH="app/models/vehicle_health_model.pkl"
   ```

4. **Start Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Monitoring

Add these endpoints to your monitoring:

- `/api/predict/health` - Check if service is ready
- `/api/predict` - Log prediction latency and success rate
- Monitor error logs for model failures

## Performance Considerations

- **Mock Predictions**: ~1ms response time
- **Model Predictions**: Depends on model complexity (typically 10-100ms)
- **Model Loading**: One-time cost at startup (typically 1-5 seconds)

## API Contract Guarantee

The API contract remains **unchanged** when transitioning from mock to real models:

✅ Same request schema
✅ Same response schema
✅ Same status codes
✅ Same error format
✅ Same endpoint paths

Only the internal implementation changes, ensuring zero breaking changes for API consumers.

## Troubleshooting

### Model not loading

```
WARNING: joblib not installed. Using mock predictions.
```

**Solution**: Install joblib
```bash
pip install joblib
```

### Model file not found

```
ERROR: Model file not found: path/to/model.pkl
```

**Solution**: Verify the model path is correct and file exists

### Predictions always using mock

Check service health:
```bash
curl http://localhost:8000/api/predict/health
# If using_mock is true, check logs for model loading errors
```

### Feature format mismatch

If predictions are wrong after loading a model, ensure:
1. Features are in correct order in `_prepare_features()`
2. Feature scaling matches model training (normalize/standardize)
3. Model expects numeric inputs

## Future Enhancements

- [ ] Model versioning and A/B testing
- [ ] Real-time model reloading without restart
- [ ] Feature engineering pipeline
- [ ] Prediction caching
- [ ] Model performance metrics collection
- [ ] Batch prediction endpoint
- [ ] Feature importance/explainability
