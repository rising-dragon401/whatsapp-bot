from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    incoming_msg = request.form.get("Body")
    response = MessagingResponse()
    msg = response.message()
    msg.body("Hello from your WhatsApp bot!")
    return response.to_xml()
