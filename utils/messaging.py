import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import logging

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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