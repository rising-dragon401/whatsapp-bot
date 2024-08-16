from fastapi import APIRouter, Response, Request, Form, HTTPException
from datetime import datetime
import logging
from typing import Union, Optional
from ai.chat import get_ai_response
from utils.messaging import send_message_to_whatsApp
from database.models.user import(
    add_user,
    retrieve_user,
    update_user,
    User,
    UserRole
)
from database.models.payment import (
    retrieve_payment,
    isSubscribed,
    Payment
)
from payment.stripe import get_payment_link
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

def handle_command(chat_id, message, from_number, to_number, group_chat=False):
    if '/start' in message:
        send_message_to_whatsApp(from_number, to_number, 'Welcome to use our service!')
        return
    elif '/help' in message:
        send_message_to_whatsApp(from_number, to_number, 'Need help with something? Send us a message @BeemoHelp')
        return 


async def handle_user_message(chat_id, message, from_number, to_number, group_chat=False):
    bot_user = await retrieve_user(chat_id)
    chat_msg = ""
    payment_link = ""    

    if bot_user is None:
        bot_user = await add_user({
            "name": "",
            "phone_number": from_number,
            "bot_number": to_number,
            "chat_id": chat_id,
            "chat_title": from_number,
            "chat_history": [],
            "userroles": UserRole.user,
            "summary": "",
            "history_cursor": 0,
            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow()),
        })
    
    isScribed = await isSubscribed(bot_user["id"])

    if bot_user["userroles"] == UserRole.user or isScribed == False:
        send_message_to_whatsApp(from_number, to_number, "Wait for a while...")
        payment_link = get_payment_link(5, userData = bot_user, creatorData = {"productName": "Restaurant Service"}, chat_id = chat_id)
    else:
        payment_link = ""

    chat_history = [] if bot_user["userroles"] == UserRole.user else bot_user["chat_history"]
    chat_history.append({"role": "user", "content": message})
    
    chat_msg = get_ai_response(chat_history, bot_user, payment_link, isScribed)

    send_message_to_whatsApp(from_number, to_number, chat_msg)

    if bot_user["userroles"] == UserRole.customer:
        chat_history.append({"role": "assistant", "content": chat_msg})
    
    await update_user({"chat_id": chat_id, "chat_history": chat_history})

@router.post("/webhook")
async def handle_bot(request: Request, From: str = Form(), To: str = Form(), WaId: str = Form(), ProfileName: Optional[str]  = Form(''), Body: Optional[str]  = Form(''), sageSid: Optional[str] = Form(None), NumMedia: Optional[int] = Form(0), MediaUrl: Optional[str] = Form(None), MediaContentType: Optional[str] = Form(None)) -> str:
    try:
        form_data = await request.form()
        bot_phone_number = To.split('+')[1]
        from_number = From
        to_number = To
        chat_id = WaId
        message = Body

        # if chat_id begins with +, remove it
        if chat_id.startswith('+'):
            chat_id = chat_id[1:]

        print('chat_id', chat_id)
    
        if (message.startswith('/')):
            handle_command(chat_id, message, from_number, to_number)
            return "success"
    
        # respond to user message
        await handle_user_message(chat_id, message, from_number, to_number)

        return "success"
    except Exception as e:
        print(e)
        return "error"

@router.get("/")
async def read_list():
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
    update_wabot = await update(wabot_id, wabot.wabot_helper())
    if update_wabot:
        return update_wabot
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")

@router.delete("/{wabot_id}", response_model=dict)
async def delete_wabot(wabot_id: str):
    success = await delete(wabot_id)
    if success:
        return {"detail": "WhatsApp Bot is deleted."}
    raise HTTPException(status_code=404, detail="WhatsApp Bot is not found.")
