import httpx
import logging

logger = logging.getLogger(__name__)


class GroqProviderError(Exception):
    pass


class GroqRateLimitError(GroqProviderError):
    pass


class GroqTimeoutError(GroqProviderError):
    pass


class GroqAPIError(GroqProviderError):
    pass


class GroqProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: int = 30,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key:
            raise GroqProviderError("Missing GROQ_API_KEY")

        if not self.model:
            raise GroqProviderError("Missing AI_MODEL")

    def generate_text(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are PulseDrive AI, an expert automotive predictive "
                        "maintenance assistant. Answer clearly, accurately, and "
                        "provide practical recommendations."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.3,
            "max_tokens": 600,
        }

        try:
            response = httpx.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )

        except httpx.TimeoutException as exc:
            raise GroqTimeoutError("Groq request timed out.") from exc

        except Exception as exc:
            raise GroqProviderError(str(exc)) from exc

        if response.status_code == 429:
            raise GroqRateLimitError("Groq rate limit exceeded.")

        if response.status_code != 200:
            logger.error(response.text)
            raise GroqAPIError(
                f"Groq API failed ({response.status_code}) : {response.text}"
            )

        data = response.json()

        try:
            return (
                data["choices"][0]["message"]["content"]
                .strip()
            )
        except Exception:
            logger.error(data)
            raise GroqAPIError("Unexpected Groq response format.")