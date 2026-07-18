from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from app.config.settings import settings


_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client


def get_database() -> Database:
    global _database
    if _database is None:
        _database = get_client()[settings.DATABASE_NAME]
    return _database
