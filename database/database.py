import os
from dotenv import load_dotenv
import motor.motor_asyncio
from bson.objectid import ObjectId

load_dotenv()

connection_strting = os.getenv("MONGO_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(connection_strting)

database = client.wabot
user_collection = database.get_collection("users")
payment_collection = database.get_collection("payments")
