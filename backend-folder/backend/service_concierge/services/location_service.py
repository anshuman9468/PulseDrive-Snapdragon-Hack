import math
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Mock database of Service Centers
SERVICE_CENTERS = [
    {
        "id": "SC-001",
        "name": "PulseDrive Care - Noida Sector 62",
        "address": "B-23, Sector 62, Noida, Uttar Pradesh 201301",
        "latitude": 28.6273,
        "longitude": 77.3725,
        "phone_number": "+919999988888",
        "operating_hours": "09:00 - 18:00",
        "available_slots": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
    },
    {
        "id": "SC-002",
        "name": "PulseDrive Care - Gurgaon Sector 14",
        "address": "12, Industrial Area, Sector 14, Gurgaon, Haryana 122001",
        "latitude": 28.4735,
        "longitude": 77.0402,
        "phone_number": "+918888877777",
        "operating_hours": "09:00 - 18:00",
        "available_slots": ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    },
    {
        "id": "SC-003",
        "name": "PulseDrive Care - Delhi Connaught Place",
        "address": "F-Block, Connaught Place, New Delhi 110001",
        "latitude": 28.6304,
        "longitude": 77.2177,
        "phone_number": "+917777766666",
        "operating_hours": "08:00 - 19:00",
        "available_slots": ["08:00", "09:00", "10:00", "12:00", "15:00", "16:00", "18:00"]
    }
]

class LocationService:
    """Service to handle coordinates, nearest service center calculations, and distance metrics."""

    def __init__(self):
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.google_maps_api_key:
            logger.warning("GOOGLE_MAPS_API_KEY is not set. Using local distance calculations.")

    def get_all_service_centers(self) -> List[Dict[str, Any]]:
        """Return all registered service centers."""
        return SERVICE_CENTERS

    def find_nearest_service_center(self, lat: float, lng: float) -> Dict[str, Any]:
        """Find the nearest service center based on haversine distance.
        
        If Google Maps API key is configured, this could be extended to use the Distance Matrix API.
        """
        nearest_center = None
        min_distance = float('inf')

        for center in SERVICE_CENTERS:
            dist = self.calculate_haversine_distance(
                lat, lng, 
                center["latitude"], center["longitude"]
            )
            if dist < min_distance:
                min_distance = dist
                nearest_center = center.copy()
        
        if nearest_center:
            nearest_center["distance_km"] = round(min_distance, 2)
            
        return nearest_center or SERVICE_CENTERS[0]

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        # Radius of the earth in km
        r = 6371.0

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
             
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
