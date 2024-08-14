from pydantic import BaseModel, Field
from database.database import payment_collection
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Payment(BaseModel):
    user_id: str = Field(...)
    paid_date: str = Field(...)
    sibscription_date: str = Field(...)
    created_at: str = Field(...)
    updated_at: str = Field(...)

def payment_helper(payment) -> dict:
    return {
        "id": str(payment["_id"]),
        "user_id": payment["user_id"],
        "paid_date": payment["paid_date"],
        "subscription_date": payment["subscription_date"],
        "created_at": payment["created_at"],
        "updated_at": payment["updated_at"]
    }

async def add_payment(payment_data: dict) -> dict:
    payment = await payment_collection.insert_one(payment_data)
    new_payment = await payment_collection.find_one({"_id": payment.inserted_id})
    return payment_helper(new_payment)

async def retrieve_payment(user_id: str) -> dict:
    payment = await payment_collection.find_one({"user_id": user_id})
    if payment:
        return payment_helper(payment)
    else:
        return None

async def update_subscription(payment_data: dict) -> dict:
    filter_query = {"user_id": payment_data["user_id"]}
    update_query = {"$set": payment_data}

    result = await payment_collection.update_one(filter_query, update_query)

    if result.matched_count == 0:
        return None
    else:
        payment = await payment_collection.find_one({"user_id": payment_data["user_id"]})
        return payment_helper(payment)

async def isSubscribed(user_id: str) -> bool:
    payment = await retrieve_payment(user_id)
    if payment:
        format1 = "%Y-%m-%d %H:%M:%S"
        subscription_date = datetime.strptime(payment["subscription_date"][:-7], format1)
        difference = relativedelta(datetime.utcnow(), subscription_date)
        return difference.days < 0
    else:
        return False