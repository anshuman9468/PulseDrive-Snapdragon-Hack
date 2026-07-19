from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, sensor, prediction, ask_ai, health, websocket, dashboard
from app.api import users
from service_concierge.routes import service_routes

app = FastAPI(
    title="Pulse Drive API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sensor.router, tags=["Sensor"])
app.include_router(prediction.router, tags=["Prediction"])
app.include_router(ask_ai.router, tags=["Ask AI"])
app.include_router(health.router, tags=["Health"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(users.router)
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(service_routes.router, prefix="/api/service", tags=["Service Concierge"])


