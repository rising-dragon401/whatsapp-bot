from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import logging
from database.models.wabots import (
    read_all_wabots,
    create_wabot,
    read_wabot,
    update_wabot,
    delete_wabot,
    WaBotDocument,
    WaBot
)

router = APIRouter(
    prefix="/api/wabots",
    tags=["wabots"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def getAllWaBots(admin_id: str, permission: str):
    wabots = await read_all_wabots(admin_id, permission)
    return wabots

@router.post("/", response_model=WaBot)
async def createWaBot(wabot: WaBot):
    wabot_doc = WaBotDocument(**wabot.model_dump())
    return await create_wabot(wabot_doc)

@router.get("/{wabot_id}", response_model=WaBot)
async def readWaBot(wabot_id: str):
    wabot = await read_wabot(wabot_id)
    if wabot:
        return wabot
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")

@router.put("/{wabot_id}", response_model=WaBot)
async def updateWaBot(wabot_id: str, wabot: WaBot):
    updatedWabot = await update_wabot(wabot_id, wabot.model_dump())
    if updatedWabot:
        return updatedWabot
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")

@router.delete("/{wabot_id}", response_model=dict)
async def deleteWaBot(wabot_id: str):
    success = await delete_wabot(wabot_id)
    if success:
        return {"detail": "WhatsApp Bot is deleted."}
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")
