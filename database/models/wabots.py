from beanie import Document
from pydantic import BaseModel
from typing import Optional

class WaBot(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    visitor: Optional[int] = 0
    bot_number: str
    system_prompt: str
    gpt_model: str
    openai_api_key: str

class WaBotDocument(Document, WaBot):
    class Settings:
        name = "wabots"

async def read_all_wabots() -> list[WaBotDocument]:
    return await WaBotDocument.find_all().to_list()

async def create_wabot(wabot: WaBotDocument) -> WaBotDocument:
    return await wabot.insert()

async def read_wabot(wabot_id: str) -> WaBotDocument:
    return await WaBotDocument.get(wabot_id)

async def update_wabot(wabot_id: str, wabot_update: dict) -> WaBotDocument:
    wabot = await WaBotDocument.get(wabot_id)
    if wabot:
        wabot = await wabot.update({"$set": wabot_update})
    return wabot

async def delete_wabot(wabot_id: str) -> bool:
    wabot = await WaBotDocument.get(wabot_id)
    if wabot:
        await wabot.delete()
        return True
    return False

async def retrieve_wabot(search_params: dict) -> WaBotDocument:
    return await WaBotDocument.find_one(search_params)

