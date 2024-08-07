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
    phone_number: str = Field(...)
    chat_title: str = Field(...)
    chat_history: dict = Field(...)
    userroles: UserRole = Field(...)
    summary: str = Field(...)
    history_cursor: int = Field(...)
    created_at: str = Field(...)
    updated_at: str = Field(...)

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "phone_number": user["phone_number"],
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

async def retrieve_user(phone_number: str) -> dict:
    user = await user_collection.find_one({"phone_number": phone_number})    
    if user:
        print("\n***** Current User *****\n", user["phone_number"])
        return user_helper(user)
    else:
        return None