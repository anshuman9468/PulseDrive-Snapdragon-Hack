import os
import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SarvamService:
    """Service wrapper for Sarvam AI APIs.
    
    Provides:
    1. Speech to Text (transcribe)
    2. Text to Speech (synthesize)
    3. Intent & Entity Understanding (extract_slots)
    """

    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.base_url = os.getenv("SARVAM_API_URL", "https://api.sarvam.ai")
        if not self.api_key:
            logger.warning("SARVAM_API_KEY environment variable is not set. Service will run in MOCK mode.")
            self.is_mock = True
        else:
            self.is_mock = False
            from sarvamai import AsyncSarvamAI
            self.client = AsyncSarvamAI(api_subscription_key=self.api_key)

    async def speech_to_text(self, audio_content: bytes, language_code: str = "en-IN") -> str:
        """Convert spoken audio bytes to text transcript."""
        if self.is_mock:
            logger.info("Sarvam STT called in mock mode")
            return "Yes, Noida Sector 62, tomorrow at 10 AM"

        try:
            response = await self.client.speech_to_text.transcribe(
                file=audio_content,
                model="saaras:v3",
                language_code=language_code
            )
            return response.transcript or ""
        except Exception as e:
            logger.error(f"Sarvam STT exception via SDK: {e}")
            # Fallback to direct request if SDK has issues
            headers = {"api-subscription-key": self.api_key}
            try:
                async with httpx.AsyncClient() as client:
                    files = {"file": ("audio.wav", audio_content, "audio/wav")}
                    data = {"model": "saarika:v2.5", "language_code": language_code}
                    res = await client.post(
                        f"{self.base_url}/speech-to-text",
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=10.0
                    )
                    if res.status_code == 200:
                        return res.json().get("transcript", "")
            except Exception as inner_e:
                logger.error(f"Sarvam STT direct fallback exception: {inner_e}")
            return "Fallback transcript"

    async def text_to_speech(self, text: str, language_code: str = "en-IN") -> bytes:
        """Convert text content to speech audio bytes."""
        if self.is_mock:
            logger.info(f"Sarvam TTS called in mock mode for text: '{text}'")
            return b"MOCK_AUDIO_DATA"

        try:
            response = await self.client.text_to_speech.convert(
                text=text,
                target_language_code=language_code,
                speaker="anushka",
                model="bulbul:v3"
            )
            if response.audios:
                import base64
                return base64.b64decode(response.audios[0])
            return b""
        except Exception as e:
            logger.error(f"Sarvam TTS exception via SDK: {e}")
            # Fallback to direct request if SDK has issues
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": [text],
                "target_language_code": language_code,
                "speaker": "meera",
                "model": "bulbul:v3"
            }
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        f"{self.base_url}/text-to-speech",
                        headers=headers,
                        json=payload,
                        timeout=10.0
                    )
                    if res.status_code == 200:
                        data = res.json()
                        import base64
                        audio_b64 = data.get("audios", [""])[0]
                        return base64.b64decode(audio_b64) if audio_b64 else b""
            except Exception as inner_e:
                logger.error(f"Sarvam TTS direct fallback exception: {inner_e}")
            return b""

    async def extract_intent_and_entities(self, text: str) -> Dict[str, Any]:
        """Analyze text to identify customer intent and slots like location, date, time."""
        # Simple rule-based slot extraction as robust fallback
        extracted = {
            "intent": "UNKNOWN",
            "location": None,
            "date": None,
            "time": None,
            "confirmation": None
        }
        
        text_lower = text.lower()
        import re
        words = set(re.findall(r'\b[a-z0-9]+\b', text_lower))
        
        # Intent Heuristics
        yes_words = {"yes", "yeah", "confirm", "sure", "book", "schedule", "okay", "ok"}
        no_words = {"no", "cancel", "deny", "stop"}
        
        if any(w in words for w in yes_words):
            extracted["intent"] = "BOOK_APPOINTMENT"
            extracted["confirmation"] = True
        elif any(w in words for w in no_words):
            extracted["intent"] = "CANCEL_OR_DECLINE"
            extracted["confirmation"] = False

        # Location extraction (e.g. Noida, Delhi, Sector 62)
        locations = ["noida sector 62", "noida", "delhi", "gurgaon", "mumbai", "bangalore"]
        for loc in locations:
            if loc in text_lower:
                extracted["location"] = loc.title()
                extracted["intent"] = "PROVIDE_LOCATION"
                break

        # Date extraction (e.g. tomorrow, monday, next week, today)
        if "tomorrow" in text_lower:
            extracted["date"] = "tomorrow"
            extracted["intent"] = "PROVIDE_DATE"
        elif "today" in text_lower:
            extracted["date"] = "today"
            extracted["intent"] = "PROVIDE_DATE"

        # Time extraction (e.g. 10 AM, 10:00, afternoon, morning)
        if "10 am" in text_lower or "10:00" in text_lower:
            extracted["time"] = "10:00"
            extracted["intent"] = "PROVIDE_TIME"
        elif "2 pm" in text_lower or "14:00" in text_lower:
            extracted["time"] = "14:00"
            extracted["intent"] = "PROVIDE_TIME"

        if self.is_mock:
            logger.info(f"Sarvam NLU (mock) analyzed: '{text}' -> {extracted}")
            return extracted

        # Call Sarvam's LLM / NLU endpoint if available
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "chat_context": [
                {"role": "system", "content": "Extract slots: location, date (YYYY-MM-DD), time (HH:MM), and booking intent from user message."}
            ],
            "message": text
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/nlu",
                    headers=headers,
                    json=payload,
                    timeout=5.0
                )
                if response.status_code == 200:
                    sarvam_extracted = response.json().get("slots", {})
                    # Merge/override with rule heuristics
                    for k, v in sarvam_extracted.items():
                        if v:
                            extracted[k] = v
        except Exception as e:
            logger.warning(f"Sarvam NLU call failed, using rule heuristics: {e}")
            
        return extracted
