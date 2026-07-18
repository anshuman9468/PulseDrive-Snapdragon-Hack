# Prediction API Testing Guide

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

### 2. Test Basic Prediction

Using `curl`:
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicleId": "VH123456",
    "features": {
      "rpm": 3000,
      "temperature": 85,
      "mileage": 45000,
      "fuel_consumption": 8.5,
      "battery_voltage": 13.5
    }
  }'
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/predict",
    json={
        "vehicleId": "VH123456",
        "features": {
            "rpm": 3000,
            "temperature": 85,
            "mileage": 45000,
            "fuel_consumption": 8.5,
            "battery_voltage": 13.5
        }
    }
)

print(response.json())
```

### 3. Check Service Health

```bash
curl "http://localhost:8000/api/predict/health"
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": false,
  "using_mock": true
}
```

## Test Cases

### Test 1: Basic Prediction
**Request:**
```json
{
  "vehicleId": "TRUCK001",
  "features": {
    "rpm": 2000,
    "temperature": 75,
    "mileage": 100000,
    "fuel_consumption": 7.5,
    "battery_voltage": 13.5
  }
}
```

**Expected Response:**
- Status: 200 OK
- `healthScore` between 0-100
- `status` one of: "healthy", "warning", "critical"
- `confidence` between 0-1

### Test 2: Minimal Request
**Request:**
```json
{
  "vehicleId": "VH999"
}
```

**Expected Response:**
- Status: 200 OK
- Valid prediction with default/mock data

### Test 3: Empty Vehicle ID (Error Case)
**Request:**
```json
{
  "vehicleId": ""
}
```

**Expected Response:**
- Status: 400 Bad Request
- Error message: "vehicleId cannot be empty"

### Test 4: Invalid Request (Error Case)
**Request:**
```json
{
  "features": {"rpm": 3000}
}
```

**Expected Response:**
- Status: 422 Unprocessable Entity
- Validation error (missing required field)

### Test 5: Deterministic Mock Results
**Request 1:**
```json
{
  "vehicleId": "VH001"
}
```

**Request 2:** (Same vehicleId)
```json
{
  "vehicleId": "VH001"
}
```

**Expected Response:**
- Both responses should have identical healthScore and status (deterministic)

### Test 6: Health Status Endpoint
**Request:**
```
GET /api/predict/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": false,
  "using_mock": true
}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Interactive documentation with live testing available.

## Expected Health Status Distribution

With mock predictions:
- Vehicle IDs with low hash: "healthy" (score 85-99)
- Vehicle IDs with medium hash: "warning" (score 60-84)
- Vehicle IDs with high hash: "critical" (score 20-59)

This ensures consistent behavior for testing while being realistic.

## Performance Expectations

- Mock predictions: ~1ms per request
- API overhead: ~10-50ms (network + FastAPI)
- Total response time: 50-100ms

## Integration with Frontend

### Example: React Component

```javascript
async function getPrediction(vehicleId, features) {
  const response = await fetch('http://localhost:8000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      vehicleId,
      features
    })
  });
  
  if (!response.ok) {
    throw new Error(`Prediction failed: ${response.statusText}`);
  }
  
  return response.json();
}

// Usage
getPrediction('TRUCK001', {
  rpm: 3000,
  temperature: 85,
  mileage: 45000,
  fuel_consumption: 8.5,
  battery_voltage: 13.5
}).then(prediction => {
  console.log(`Health: ${prediction.healthScore}%`);
  console.log(`Status: ${prediction.status}`);
  console.log(`Recommendation: ${prediction.recommendation}`);
});
```

## Debugging

### Enable Debug Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

Or modify `app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

Watch for:
- Model loading messages
- Prediction errors
- Fallback to mock warnings

### Common Issues

**Issue**: All predictions return "pending"
- **Solution**: Update FastAPI and restart server

**Issue**: CORS errors in browser
- **Solution**: Already configured in main.py, should work out of the box

**Issue**: Slow responses
- **Solution**: Check system resources, profiles with Python profiler if needed

## Load Testing

### Using Apache Bench

```bash
# Single request benchmark
ab -n 1000 -c 10 -p payload.json -T application/json http://localhost:8000/api/predict

# Where payload.json contains:
# {"vehicleId": "VH001", "features": {"rpm": 3000}}
```

### Using wrk (more advanced)

```bash
wrk -t4 -c100 -d30s --script post.lua http://localhost:8000/api/predict

# post.lua:
# request = function()
#    wrk.method = "POST"
#    wrk.body = '{"vehicleId": "VH001", "features": {}}'
#    wrk.headers["Content-Type"] = "application/json"
#    return wrk.format(nil)
# end
```

## Next Steps

1. **Transition to Real Model**: Place `model.pkl` in `app/models/` and restart
2. **Add Caching**: Implement Redis caching for frequently requested vehicles
3. **Add Monitoring**: Set up logging, metrics, and alerts
4. **Add Batch Endpoint**: Create `/api/predict/batch` for fleet predictions
5. **Add Authentication**: Secure endpoints with API keys or JWT tokens
