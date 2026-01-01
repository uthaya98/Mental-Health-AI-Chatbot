from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)

# Database name is embedded in URI
db = client.get_default_database()

users_collection = db["users"]
sessions_collection = db["sessions"]
messages_collection = db["messages"]


def get_database():
    return db
