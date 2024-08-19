from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    customer = "customer"

class User(BaseModel):
    chat_id: str = Field(...)
    name: str = Field(...)
    phone_number: str = Field(...)
    bot_number: str = Field(...)
    bot_id: str = Field(...)
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
        "bot_id": user["bot_id"],
        "chat_id": user["chat_id"],
        "chat_title": user["chat_title"],
        "chat_history": user["chat_history"],
        "userroles": user["userroles"],
        "summary": user["summary"],
        "history_cursor": user["history_cursor"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }

class UserDocument(Document, User):
    class Settings:
        name = "users"

async def add_user(user: UserDocument) -> UserDocument:
    return await user.insert()

async def retrieve_user(chat_id: str) -> UserDocument:
    return await UserDocument.find_one({"chat_id": chat_id})

async def update_user(user_data: dict) -> UserDocument:
    user = await UserDocument.find_one({"chat_id": user_data["chat_id"]})
    if user:
        user = await user.update({"$set": user_data})
    return user