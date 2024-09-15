from motor.motor_asyncio import AsyncIOMotorClient

from config import Config

connection = AsyncIOMotorClient(Config.MONGO_URL)
data = connection.neko
