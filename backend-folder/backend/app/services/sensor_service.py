from datetime import datetime
from typing import Any, Optional, Union

from pymongo import DESCENDING
from pymongo.collection import Collection

from app.config.database import get_database
from app.models.sensor import SensorData


class SensorService:
    """Service layer for vehicle sensor data persistence and retrieval."""

    def __init__(self) -> None:
        self.collection: Collection = get_database()["sensor_data"]

    def save_sensor_data(self, data: Union[SensorData, dict[str, Any]]) -> dict[str, Any]:
        """
        Persist a sensor reading to the sensor_data collection.

        Converts the Pydantic model or dict to a MongoDB-compatible document before insert.
        """
        if isinstance(data, dict):
            # Generate timestamp if missing
            if "timestamp" not in data or data["timestamp"] is None:
                data["timestamp"] = datetime.utcnow()
            # Validate against SensorData model to validate nested objects
            validated_data = SensorData.model_validate(data)
            document = validated_data.model_dump(mode="python")
        else:
            if data.timestamp is None:
                data.timestamp = datetime.utcnow()
            document = data.model_dump(mode="python")

        result = self.collection.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    def get_live_sensor_data(self) -> Optional[dict[str, Any]]:
        """Return the latest sensor document sorted by timestamp."""
        document = self.collection.find_one(sort=[("timestamp", DESCENDING)])
        if document is None:
            return None
        return self._serialize_document(document)

    def get_sensor_history(
        self, vehicle_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Return the latest 100 sensor records sorted by timestamp.

        Optionally filter by vehicle_id when provided.
        """
        query: dict[str, Any] = {}
        if vehicle_id:
            query["vehicleId"] = vehicle_id

        cursor = (
            self.collection.find(query)
            .sort("timestamp", DESCENDING)
            .limit(100)
        )
        return [self._serialize_document(document) for document in cursor]

    @staticmethod
    def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
        """Convert MongoDB document fields to JSON-serializable values."""
        serialized = dict(document)
        if "_id" in serialized:
            serialized["_id"] = str(serialized["_id"])
        return serialized
