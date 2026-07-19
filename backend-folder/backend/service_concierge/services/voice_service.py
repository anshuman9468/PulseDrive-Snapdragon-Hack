import logging
from typing import Optional, Dict, Any

from service_concierge.agents.conversation_agent import ConversationAgent
from service_concierge.services.twilio_service import TwilioService
from service_concierge.services.sarvam_service import SarvamService

logger = logging.getLogger(__name__)

class VoiceService:
    """Bridges Twilio Call Events and Sarvam NLU to run interactive voice concierge calls."""

    def __init__(
        self,
        conversation_agent: ConversationAgent,
        twilio_service: TwilioService,
        sarvam_service: SarvamService
    ):
        self.conversation_agent = conversation_agent
        self.twilio_service = twilio_service
        self.sarvam_service = sarvam_service

    async def handle_call_start(self, vehicle_id: str, phone_number: str, gather_url: str) -> str:
        """Invoked when Twilio call starts. Sets up initial conversation and returns TwiML XML."""
        conv = await self.conversation_agent.get_or_create_conversation(vehicle_id, phone_number)
        initial_prompt = conv.history[0].content
        
        logger.info(f"Answering voice call for vehicle {vehicle_id}. Prompt: '{initial_prompt}'")
        return self.twilio_service.generate_twiml_response(initial_prompt, gather_url)

    async def handle_speech_input(self, conversation_id: str, speech_result: str, gather_url: str) -> str:
        """Invoked when Twilio gathers speech text from user.
        
        Args:
            conversation_id: Active conversation ID
            speech_result: Transcribed text from Twilio/Sarvam
            gather_url: The webhook callback URL for the next turn
            
        Returns:
            TwiML XML response containing next speech audio
        """
        logger.info(f"Voice session {conversation_id} received input: '{speech_result}'")
        
        # Feed turn to conversation agent
        reply_text = await self.conversation_agent.process_turn(conversation_id, speech_result)
        
        # Check if conversation is still active
        conv = self.conversation_agent.repository.get_conversation(conversation_id)
        is_active = conv.state.is_active if conv else False
        
        if is_active:
            return self.twilio_service.generate_twiml_response(reply_text, gather_url)
        else:
            # End call gracefully
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{reply_text}</Say>
    <Hangup />
</Response>"""
            return twiml
            
    async def process_raw_audio_chunk(self, conversation_id: str, audio_bytes: bytes) -> bytes:
        """Transforms streaming raw audio chunks via Sarvam STT -> Agent -> Sarvam TTS."""
        # Step 1: Transcribe
        transcript = await self.sarvam_service.speech_to_text(audio_bytes)
        
        # Step 2: Dialogue Agent Turn
        reply_text = await self.conversation_agent.process_turn(conversation_id, transcript)
        
        # Step 3: Synthesize Speech response
        response_audio = await self.sarvam_service.text_to_speech(reply_text)
        
        return response_audio
