import logging
import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from pymongo import MongoClient, DESCENDING

from app.config.settings import settings

logger = logging.getLogger(__name__)

class InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.documents = []

    def insert_one(self, document: dict) -> Any:
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        # Make a copy so edits don't mutate original
        doc_copy = dict(document)
        self.documents.append(doc_copy)
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertOneResult(doc_copy["_id"])

    def find_one(self, filter: Optional[dict] = None, sort: Optional[list] = None) -> Optional[dict]:
        docs = self._filter_and_sort(filter, sort)
        return dict(docs[0]) if docs else None

    def find(self, filter: Optional[dict] = None) -> Any:
        docs = self._filter_and_sort(filter, None)
        class Cursor:
            def __init__(self, documents):
                self.documents = documents
            def sort(self, key_or_list, direction=None):
                if isinstance(key_or_list, list):
                    sort_key = key_or_list[0][0]
                    descending = key_or_list[0][1] == -1 or key_or_list[0][1] == DESCENDING
                else:
                    sort_key = key_or_list
                    descending = direction == -1 or direction == DESCENDING
                
                # Sort helper handling datetimes/None
                def sort_key_fn(x):
                    val = x.get(sort_key)
                    if val is None:
                        return datetime.min
                    return val
                
                self.documents.sort(key=sort_key_fn, reverse=descending)
                return self
            def limit(self, num):
                self.documents = self.documents[:num]
                return self
            def __iter__(self):
                return iter(self.documents)
        return Cursor(docs)

    def update_one(self, filter: dict, update: dict, upsert: bool = False) -> Any:
        docs = self._filter_and_sort(filter, None)
        if not docs and upsert:
            new_doc = dict(filter)
            if "_id" not in new_doc:
                new_doc["_id"] = str(uuid.uuid4())
            self.documents.append(new_doc)
            docs = [new_doc]
        if docs:
            doc = docs[0]
            if isinstance(update, dict):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        doc[k] = v
                else:
                    for k, v in update.items():
                        doc[k] = v
        class UpdateResult:
            def __init__(self, modified_count):
                self.modified_count = modified_count
        return UpdateResult(1 if docs else 0)

    def _filter_and_sort(self, filter: Optional[dict], sort: Optional[list]) -> list:
        results = []
        filter = filter or {}
        for doc in self.documents:
            match = True
            for k, v in filter.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(dict(doc))
        if sort:
            if isinstance(sort, list):
                sort_key = sort[0][0]
                descending = sort[0][1] == -1 or sort[0][1] == DESCENDING
            else:
                sort_key = sort
                descending = True
            
            def sort_key_fn(x):
                val = x.get(sort_key)
                if val is None:
                    return datetime.min
                return val

            results.sort(key=sort_key_fn, reverse=descending)
        return results

class InMemoryDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self.collections:
            self.collections[name] = InMemoryCollection(name)
        return self.collections[name]

    def command(self, cmd: str, **kwargs) -> dict:
        if cmd == "ping":
            return {"ok": 1.0}
        raise NotImplementedError(f"Command {cmd} is not implemented in memory database")

_client: Optional[MongoClient] = None
_database: Optional[Any] = None

def get_client() -> Any:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1000)
    return _client

def get_database() -> Any:
    global _database
    if _database is None:
        try:
            client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1000)
            client.admin.command('ping')
            _database = client[settings.DATABASE_NAME]
            logger.info("Connected to MongoDB database successfully.")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Falling back to in-memory database store.")
            _database = InMemoryDatabase()
    return _database
