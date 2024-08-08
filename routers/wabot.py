from fastapi import APIRouter, Response, Request, Form
import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime
import logging
from typing import Union, Optional
from ai.chat import get_ai_response
from database.models.user import(
    add_user,
    retrieve_user,
    update_user,
    User,
    UserRole
)
from payment.stripe import get_payment_link


router = APIRouter(
    prefix="/api/wabot",
    tags=["wabot"],
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def send_message_to_whatsApp(to_number, from_number, body = '', url = ''):
    try:
        if url == '':
            message = client.messages.create(
                    from_=from_number,
                    body=f'{body}',
                    to=to_number,
                )
        else: 
            message = client.messages.create(
                    from_=from_number,
                    body=f'{body}',
                    media_url=f'{url}',
                    to=to_number,
                )
        
        logger.info(f"Message sent to {to_number}: {message.body} {url}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")

def handle_command(chat_id, bot_phone_number, user_name, message, from_number, to_number, group_chat=False):
    print("Handling Command")

    if '/start' in message:
        send_message_to_whatsApp(from_number, to_number, 'Welcome to use our service!')
        return
    elif '/help' in message:
        send_message_to_whatsApp(from_number, to_number, 'Need help with something? Send us a message @BeemoHelp')
        return 


async def handle_user_message(chat_id, bot_phone_number, message, from_number, to_number, group_chat=False):
    print("\n**********CURRENT TIME**********\n", datetime.now().timestamp())
    print(message)

    print("\n***Phone Number***\n", from_number)

    bot_user = await retrieve_user(chat_id)
    chat_msg = ""
    payment_link = ""

    if bot_user is None:
        print("Save User\n")
        bot_user = await add_user({
            "phone_number": from_number,
            "chat_id": chat_id,
            "chat_title": from_number,
            "chat_history": [],
            "userroles": UserRole.user,
            "summary": "",
            "history_cursor": 0,
            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow()),
        })
        
    if bot_user["userroles"] == UserRole.user:
        payment_link = get_payment_link(amount=20, userData = bot_user, creatorData = {"productName": "Restaurant Service", "bot_number": bot_phone_number}, chat_id = chat_id)

    chat_history = bot_user["chat_history"]
    chat_history.append({"role": "user", "content": message})
    
    chat_msg = get_ai_response(chat_history, bot_user, payment_link)
    chat_history.append({"role": "assistant", "content": chat_msg})

    await update_user({"phone_number": from_number, "chat_history": chat_history})

    send_message_to_whatsApp(from_number, to_number, chat_msg)

@router.post("/webhook")
async def handle_bot(request: Request, From: str = Form(), To: str = Form(), WaId: str = Form(), ProfileName: Optional[str]  = Form(''), Body: Optional[str]  = Form(''), sageSid: Optional[str] = Form(None), NumMedia: Optional[int] = Form(0), MediaUrl: Optional[str] = Form(None), MediaContentType: Optional[str] = Form(None)) -> str:
    try:
        form_data = await request.form()
        user_name = ProfileName
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
            handle_command(chat_id, bot_phone_number, user_name, message, from_number, to_number)
            return "success"
    
        # respond to user message
        await handle_user_message(chat_id, bot_phone_number, message, from_number, to_number)

        return "success"
    except Exception as e:
        print(e)
        return "error"
