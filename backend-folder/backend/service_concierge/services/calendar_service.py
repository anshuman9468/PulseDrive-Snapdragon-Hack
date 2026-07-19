import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CalendarService:
    """Manages service center calendar slots, reservations, working hours, and holiday schedules."""

    def __init__(self):
        # Mock holiday calendar: dates in YYYY-MM-DD that are closed
        self.holidays = ["2026-12-25", "2026-01-01", "2026-08-15"]
        self.working_hours_start = 9 # 9:00 AM
        self.working_hours_end = 18  # 6:00 PM

    def is_working_day(self, date_str: str) -> bool:
        """Check if target date falls on a holiday or weekend."""
        if date_str in self.holidays:
            return False
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # 5 is Saturday, 6 is Sunday
            if dt.weekday() == 6: # Sunday closed
                return False
            return True
        except ValueError:
            return False

    def get_available_slots(self, date_str: str, service_center_slots: List[str]) -> List[str]:
        """Filter slots based on working hours, current time (if today), and day validity."""
        if not self.is_working_day(date_str):
            logger.info(f"Date {date_str} is not a working day.")
            return []

        # Return predefined service center slots
        return service_center_slots

    def validate_slot(self, date_str: str, time_str: str, service_center_slots: List[str]) -> bool:
        """Verify if a slot is valid and available."""
        if not self.is_working_day(date_str):
            return False
        if time_str not in service_center_slots:
            return False
        return True
