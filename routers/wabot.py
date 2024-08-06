from fastapi import APIRouter, Response, Request, Form
import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime
import logging
from typing import Union, Optional
from ai.chat import get_ai_response

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


async def handle_user_message(chat_id, bot_phone_number, message, from_number, to_number, group_chat=False):
    print("\n**********CURRENT TIME**********\n", message)
    print(datetime.now().timestamp())

    get_ai_response([{"role": "user", "content": message}])

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
