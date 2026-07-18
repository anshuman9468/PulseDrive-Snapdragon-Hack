# Pulse Drive Backend

Pulse Drive is a scalable backend foundation built with FastAPI, PyMongo, JWT authentication readiness, and WebSocket support. This repository provides the core architecture for a future vehicle monitoring and predictive system.

## Folder Structure

backend/
├── app/
│   ├── api/                # API router modules
│   │   ├── auth.py
│   │   ├── sensor.py
│   │   ├── prediction.py
│   │   ├── ask_ai.py
│   │   └── health.py
│   ├── config/             # Configuration and database utilities
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/             # Pydantic request and response models
│   │   ├── user.py
│   │   ├── sensor.py
│   │   ├── prediction.py
│   │   └── alert.py
│   ├── services/           # Service layer skeletons
│   │   ├── auth_service.py
│   │   ├── sensor_service.py
│   │   └── prediction_service.py
│   ├── websocket/          # WebSocket connection manager
│   │   └── manager.py
│   │   
│   └── main.py             # FastAPI application entrypoint
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

## Setup Instructions

1. Install Python 3.12.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update values as needed.

## Run Instructions

Start the server from the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Environment Variables

- `MONGO_URI`: MongoDB connection string.
- `DATABASE_NAME`: Primary MongoDB database name.
- `SECRET_KEY`: JWT secret key.
- `ALGORITHM`: JWT signing algorithm.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time.

## API List

- `POST /api/auth/register` - Register a new user.
- `POST /api/auth/login` - Authenticate a user and obtain a JWT token.
- `POST /api/sensor-data` - Submit sensor telemetry data.
- `GET /api/live` - Retrieve live sensor data placeholders.
- `GET /api/history` - Retrieve historical sensor data placeholders.
- `POST /api/predict` - Submit a prediction request.
- `POST /api/ask-ai` - Submit an AI inquiry request placeholder.
- `GET /health` - Health check endpoint.
