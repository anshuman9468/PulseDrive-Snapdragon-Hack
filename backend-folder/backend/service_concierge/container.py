import logging
from service_concierge.repository.booking_repository import BookingRepository
from service_concierge.services.location_service import LocationService
from service_concierge.services.calendar_service import CalendarService
from service_concierge.services.scheduler_service import SchedulerService
from service_concierge.services.twilio_service import TwilioService
from service_concierge.services.sarvam_service import SarvamService
from service_concierge.services.notification_service import NotificationService
from service_concierge.services.booking_service import BookingService
from service_concierge.agents.conversation_agent import ConversationAgent
from service_concierge.agents.alert_agent import AlertAgent
from service_concierge.services.voice_service import VoiceService
from service_concierge.services.outbound_call_service import OutboundCallService

logger = logging.getLogger(__name__)

class ServiceConciergeContainer:
    """Dependency injection container initializing Service Concierge singletons."""

    def __init__(self):
        logger.info("Initializing Service Concierge Container dependencies")
        
        self.repository = BookingRepository()
        self.location_service = LocationService()
        self.calendar_service = CalendarService()
        
        self.scheduler_service = SchedulerService(
            repository=self.repository,
            location_service=self.location_service,
            calendar_service=self.calendar_service
        )
        
        self.twilio_service = TwilioService()
        self.outbound_call_service = OutboundCallService()
        self.sarvam_service = SarvamService()

        
        self.notification_service = NotificationService(
            twilio_service=self.twilio_service
        )
        
        self.booking_service = BookingService(
            repository=self.repository,
            scheduler_service=self.scheduler_service,
            notification_service=self.notification_service
        )
        
        self.conversation_agent = ConversationAgent(
            repository=self.repository,
            booking_service=self.booking_service,
            sarvam_service=self.sarvam_service
        )
        
        self.alert_agent = AlertAgent(
            booking_service=self.booking_service
        )
        
        self.voice_service = VoiceService(
            conversation_agent=self.conversation_agent,
            twilio_service=self.twilio_service,
            sarvam_service=self.sarvam_service
        )

# Instantiate global container instance
container = ServiceConciergeContainer()
