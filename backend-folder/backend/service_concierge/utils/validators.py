import re
from datetime import datetime
from typing import Optional

def validate_phone_number(phone: str) -> bool:
    """Validate E.164 phone number format (e.g., +12345678901)."""
    if not phone:
        return False
    # Basic E.164 format check: '+' followed by 10 to 15 digits
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))

def validate_date(date_str: str) -> Optional[datetime]:
    """Validate and parse date string (YYYY-MM-DD)."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def validate_time(time_str: str) -> bool:
    """Validate time string (HH:MM)."""
    pattern = r"^(0\d|1\d|2[0-3]):[0-5]\d$"
    return bool(re.match(pattern, time_str))

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude (-90 to 90) and longitude (-180 to 180)."""
    return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0
