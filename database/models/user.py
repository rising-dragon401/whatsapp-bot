from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from database.database import user_collection

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    customer = "customer"

class User(BaseModel):
    chat_id: str = Field(...)
    name: str = Field(...)
    phone_number: str = Field(...)
    bot_number: str = Field(...)
    chat_title: str = Field(...)
    chat_history: list = Field(...)
    userroles: UserRole = Field(...)
    summary: str = Field(...)
    history_cursor: int = Field(...)
    created_at: str = Field(...)
    updated_at: str = Field(...)

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone_number": user["phone_number"],
        "bot_number": user["bot_number"],
        "chat_id": user["chat_id"],
        "chat_title": user["chat_title"],
        "chat_history": user["chat_history"],
        "userroles": user["userroles"],
        "summary": user["summary"],
        "history_cursor": user["history_cursor"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }

async def add_user(user_data: dict) -> dict:
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

async def retrieve_user(chat_id: str) -> dict:
    user = await user_collection.find_one({"chat_id": chat_id})    
    if user:
        return user_helper(user)
    else:
        return None

async def update_user(user_data: dict) -> dict:
    filter_query = {"chat_id": user_data["chat_id"]}
    update_query = {"$set": user_data}

    result = await user_collection.update_one(filter_query, update_query)

    if result.matched_count == 0:
        return None
    else:
        user = await user_collection.find_one({"chat_id": user_data["chat_id"]})
        return user_helper(user)
