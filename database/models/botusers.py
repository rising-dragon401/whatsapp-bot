from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    customer = "customer"

class BotUser(BaseModel):
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

class BotUserDocument(Document, BotUser):
    class Settings:
        name = "users"

async def read_all_botusers(bot_id: str) -> list[BotUserDocument]:
    if  len(bot_id) == 0:
        return await BotUserDocument.find_all().to_list()
    else:
        return await BotUserDocument.find({"bot_id": bot_id}).to_list()

async def create_botuser(botuser: BotUserDocument) -> BotUserDocument:
    return await botuser.insert()

async def read_botuser(botuser_id: str) -> BotUserDocument:
    return await BotUserDocument.get(botuser_id)

async def update_botuser(botuser_data: dict) -> BotUserDocument:
    bot_user = await BotUserDocument.find_one({"chat_id": botuser_data["chat_id"]})
    if bot_user:
        bot_user = await bot_user.update({"$set": botuser_data})
    return bot_user

async def delete_botuser(botuser_id: str) -> bool:
    bot_user = await BotUserDocument.get(botuser_id)
    if bot_user:
        await bot_user.delete()
        return True
    return False

async def retrieve_botuser(search_params: dict) -> BotUserDocument:
    return await BotUserDocument.find_one(search_params)

