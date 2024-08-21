from pydantic import BaseModel, Field
from datetime import datetime
from dateutil.relativedelta import relativedelta
from beanie import Document

class Payment(BaseModel):
    user_id: str = Field(...)
    bot_id: str = Field(...)
    paid_date: str = Field(...)
    subscription_date: str = Field(...)
    created_at: str = Field(...)
    updated_at: str = Field(...)

class PaymentDocument(Document, Payment):
    class Settings:
        name = "payments"

async def create_payment(payment: PaymentDocument) -> PaymentDocument:
    return await payment.insert()

async def retrieve_payment(searchParams: dict) -> PaymentDocument:
    return await PaymentDocument.find_one(searchParams)    

async def update_subscription(payment_data: dict) -> PaymentDocument:
    payment = await PaymentDocument.find_one({"user_id": payment_data["user_id"]})
    if  payment:
        payment = await payment.update({"$set": payment_data})

    return payment

async def isSubscribed(user_id: str) -> bool:
    payment = await PaymentDocument.find_one({"user_id": user_id})
    if payment:
        format1 = "%Y-%m-%d %H:%M:%S"
        subscription_date = datetime.strptime(payment.subscription_date[:-7], format1)
        difference = relativedelta(datetime.utcnow(), subscription_date)
        return difference.days < 0
    else:
        return False