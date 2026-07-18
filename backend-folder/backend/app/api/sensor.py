from fastapi import APIRouter, HTTPException, Query
from pymongo import DESCENDING

from app.config.database import get_database
from app.models.sensor import SensorData

router = APIRouter(prefix="/api", tags=["Sensor"])

# MongoDB Collection
db = get_database()
sensor_collection = db["sensor_data"]


@router.post("/sensor-data")
async def create_sensor_data(sensor_data: SensorData):
    """
    Store incoming sensor data in MongoDB
    """

    try:
        data = sensor_data.model_dump()

        result = sensor_collection.insert_one(data)

        return {
            "success": True,
            "message": "Sensor data stored successfully",
            "inserted_id": str(result.inserted_id),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live")
async def get_live_sensor_data():
    """
    Fetch latest sensor reading
    """

    try:
        latest = sensor_collection.find_one(
            sort=[("timestamp", DESCENDING)]
        )

        if latest is None:
            raise HTTPException(
                status_code=404,
                detail="No sensor data found."
            )

        latest["_id"] = str(latest["_id"])

        return {
            "success": True,
            "data": latest
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_sensor_history(
    vehicleId: str | None = Query(default=None)
):
    """
    Fetch complete sensor history.
    If vehicleId is provided then filter by vehicle.
    """

    try:

        query = {}

        if vehicleId:
            query["vehicleId"] = vehicleId

        data = list(
            sensor_collection.find(query).sort(
                "timestamp",
                DESCENDING
            )
        )

        for item in data:
            item["_id"] = str(item["_id"])

        return {
            "success": True,
            "count": len(data),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))