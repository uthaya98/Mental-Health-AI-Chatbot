import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

logger = logging.getLogger("mental-health-ai")

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_database() -> Optional[Database]:
    """
    Lazily initialize MongoDB so startup does not crash
    when DNS/URI is unavailable in some environments.
    """
    global _client, _db

    if _db is not None:
        return _db

    try:
        _client = MongoClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=3000,
            connect=False,
        )
        _db = _client.get_default_database()
    except Exception as exc:
        logger.error("Mongo initialization failed: %s", exc)
        _client = None
        _db = None

    return _db
