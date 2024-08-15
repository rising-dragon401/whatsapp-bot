import motor.motor_asyncio
from bson.objectid import ObjectId
from config import CONFIG

connection_strting = CONFIG.mongo_uri

client = motor.motor_asyncio.AsyncIOMotorClient(connection_strting)

database = client.wabot
user_collection = database.get_collection("users")
payment_collection = database.get_collection("payments")
