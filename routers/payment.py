from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import stripe
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.messaging import send_message_to_whatsApp
from database.models.user import(
    update_user,
    UserRole
)
from database.models.payment import(
    add_payment,
    retrieve_payment,
    update_subscription
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
            print("***** Payment Was Successful *****")
            metadata = session.metadata
            chatId = metadata["chatId"]
            userId = metadata["userId"]

            await update_user({
                "chat_id": chatId,
                "userroles": UserRole.customer,
                "updated_at": str(datetime.utcnow()),
            })

            payment = await retrieve_payment(userId)

            paid_date = datetime.utcnow()
            scribed_date = paid_date + relativedelta(months = 1)

            if payment is None:
                print("\n***** Add User's Payment Information *****\n")
                payment = await add_payment({
                    "user_id": userId,
                    "paid_date": str(paid_date),
                    "subscription_date": str(scribed_date),
                    "created_at": str(datetime.utcnow()),
                    "updated_at": str(datetime.utcnow()),
                })
            else:
                print("\n***** Update User's subscription *****\n")
                payment = await update_subscription({
                    "user_id": userId,
                    "paid_date": str(paid_date),
                    "subscription_date": str(scribed_date),
                    "updated_at": str(datetime.utcnow()),
                })

            print("\n***** Phone Number *****\n", metadata["phone_number"])
            print("\n***** Bot Number *****\n", metadata["bot_number"])

            send_message_to_whatsApp(metadata["phone_number"], metadata["bot_number"], body='Payment was successful.')

            return RedirectResponse(url="/payment-success")
        else:
            raise HTTPException(status_code=400, detail="Payment was not successful")
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))