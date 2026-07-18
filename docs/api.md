# PulseDrive — API Reference

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### `GET /`

Root endpoint. Returns service metadata.

**Response:**
```json
{
  "service": "PulseDrive API",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### `GET /health`

Global health check.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": false,
  "runtime": "cpu"
}
```

---

### `GET /api/health`

API router health check.

**Response:**
```json
{
  "status": "ok",
  "router": "api",
  "version": "0.1.0"
}
```

---

### `POST /api/predict`

Analyze vehicle sensor data and return a health prediction.

**Request Body:**
```json
{
  "temperature": 42.0,
  "current": 1.4,
  "smoke": 0,
  "vibration": 0.32,
  "speed": 18.0
}
```

**Field Reference:**

| Field       | Type  | Description                              | Constraints    |
|-------------|-------|------------------------------------------|----------------|
| temperature | float | Battery/engine temp (°C)                 | Required       |
| current     | float | Electrical current draw (A)              | Required       |
| smoke       | int   | Smoke sensor (0=none, 1=detected)        | 0 or 1         |
| vibration   | float | Vibration magnitude (g-force)            | Required       |
| speed       | float | Vehicle speed (km/h)                     | ≥ 0            |

**Response:**
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

**Response Field Reference:**

| Field          | Type   | Description                              |
|----------------|--------|------------------------------------------|
| prediction     | string | NORMAL / WARNING / CRITICAL              |
| confidence     | float  | Model confidence [0.0, 1.0]              |
| health_score   | int    | Vehicle health score [0, 100]            |
| risk           | string | LOW / MEDIUM / HIGH / CRITICAL           |
| summary        | string | Human-readable prediction summary        |
| recommendation | string | Actionable advice                        |

---

### `WebSocket /ws/stream`

Real-time sensor data streaming (**Future — not yet implemented**).

**Client → Server:**
```json
{
  "temperature": 42.0,
  "current": 1.4,
  "smoke": 0,
  "vibration": 0.32,
  "speed": 18.0
}
```

**Server → Client:**
```json
{
  "prediction": "NORMAL",
  "confidence": 0.98,
  "health_score": 100,
  "risk": "LOW"
}
```

---

## Interactive Docs

Available at: `http://localhost:8000/docs` (Swagger UI)
