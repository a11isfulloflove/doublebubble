from motor.motor_asyncio import AsyncIOMotorClient

from .config import MONGO_COLLECTION, MONGO_DB_NAME, MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION]
