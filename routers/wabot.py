from fastapi import APIRouter, Depends, HTTPException
from middleware.jwtauth import JWTAuthMiddleware
from starlette.requests import Request
import logging
from database.models.wabot import (
    readall,
    create,
    read,
    update,
    delete,
    WaBotDocument,
    WaBot
) 

router = APIRouter(
    prefix="/api/wabot",
    tags=["wabot"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def read_list(request: Request):
    wabots = await readall()
    return wabots

@router.post("/", response_model=WaBot)
async def create_new_bot(wabot: WaBot):
    wabot_doc = WaBotDocument(**wabot.dict())
    return await create(wabot_doc)

@router.get("/{wabot_id}", response_model=WaBot)
async def read_wabot(wabot_id: str):
    wabot = await read(wabot_id)
    if wabot:
        return wabot
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")

@router.put("/{wabot_id}", response_model=WaBot)
async def update_wabot(wabot_id: str, wabot: WaBot):
    update_wabot = await update(wabot_id, wabot.dict())
    if update_wabot:
        return update_wabot
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")

@router.delete("/{wabot_id}", response_model=dict)
async def delete_wabot(wabot_id: str):
    success = await delete(wabot_id)
    if success:
        return {"detail": "WhatsApp Bot is deleted."}
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")
