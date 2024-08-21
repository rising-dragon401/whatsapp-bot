from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import logging
from database.models.user import (
    read_all_with_botid,
    get_user,
    User
)

router = APIRouter(
    prefix="/api/user",
    tags=["users"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def read_list_with_botid(bot_id: str):
    users = await read_all_with_botid(bot_id)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str):
    user = await get_user(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")