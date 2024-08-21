from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import logging
from database.models.botusers import (
    read_all_botusers,
    read_botuser,
    BotUser
)

router = APIRouter(
    prefix="/api/botusers",
    tags=["botusers"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def get_all_botusers_with_botid(bot_id: str):
    botusers = await read_all_botusers(bot_id)
    return botusers

@router.get("/{botuser_id}", response_model=BotUser)
async def get_botuser(botuser_id: str):
    botuser = await read_botuser(botuser_id)
    if botuser:
        return botuser
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")