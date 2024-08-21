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

class UserDocument(Document, User):
    class Settings:
        name = "users"

async def read_all() -> list[UserDocument]:
    return await UserDocument.find_all().to_list()

async def read_all_with_botid(bot_id: str) -> list[UserDocument]:
    return await UserDocument.find({"bot_id": bot_id}).to_list()

async def get_user(user_id: str) -> UserDocument:
    return await UserDocument.get(user_id)

async def add_user(user: UserDocument) -> UserDocument:
    return await user.insert()

async def retrieve_user(chat_id: str) -> UserDocument:
    return await UserDocument.find_one({"chat_id": chat_id})

async def update_user(user_data: dict) -> UserDocument:
    user = await UserDocument.find_one({"chat_id": user_data["chat_id"]})
    if user:
        user = await user.update({"$set": user_data})
    return user