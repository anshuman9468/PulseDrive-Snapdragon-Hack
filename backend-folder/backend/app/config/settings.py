import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")


class Settings:
    def __init__(self):
        self.MONGO_URI = os.getenv("MONGO_URI")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "PulseDrive")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.AI_MODEL = os.getenv("AI_MODEL")
        self.GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/v1")


settings = Settings()

