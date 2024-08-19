from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import stripe
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ai.chat import get_ai_response
from utils.messaging import send_message_to_whatsApp
from database.models.user import(
    update_user,
    UserRole
)
from database.models.payment import(
    add_payment,
    retrieve_payment,
    update_subscription,
    PaymentDocument
)

router = APIRouter(
    prefix="/api/payment",
    tags=["payment"],
)

@router.get("/success")
async def handle_payment_success(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == 'paid':
            metadata = session.metadata
            chatId = metadata["chatId"]
            userId = metadata["userId"]
            botId = metadata["botId"]

            user = await update_user({
                "chat_id": chatId,
                "userroles": UserRole.customer,
                "updated_at": str(datetime.utcnow()),
            })

            payment = await retrieve_payment(userId)

            paid_date = datetime.utcnow()
            scribed_date = paid_date + relativedelta(months = 1)

            if payment is None:
                payment = await add_payment(PaymentDocument(
                    user_id = userId,
                    bot_id = botId,
                    paid_date = str(paid_date),
                    subscription_date = str(scribed_date),
                    created_at = str(datetime.utcnow()),
                    updated_at = str(datetime.utcnow()),
                ))
            else:
                payment = await update_subscription({
                    "user_id": userId,
                    "paid_date": str(paid_date),
                    "subscription_date": str(scribed_date),
                    "updated_at": str(datetime.utcnow()),
                })

            send_message_to_whatsApp(metadata["phone_number"], metadata["bot_number"], body='Payment was successful.')

            chat_history = user.chat_history
            last_history = "" if len(chat_history) == 0 else chat_history[-1]
            if last_history["role"] == "user":
                chat_msg = get_ai_response(chat_history, user, "", True)
                send_message_to_whatsApp(metadata["phone_number"], metadata["bot_number"], body=chat_msg)

            return JSONResponse(content={"message": "Your payment was successful!", "success": "true"}, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Payment was not successful")
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))