import os
import stripe
# from db.models.user.user import User
from utils.shorten import get_shorten_url
from dotenv import load_dotenv
from database.models.user import(
    add_user,
    retrieve_user,
    User,
    UserRole
)

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

def update_user_after_charge(chat_id, charge_id, email='', creator=None, user=None):
    print('UPDATING USER')

    # get charge data
    charge = stripe.Charge.retrieve(charge_id)

    print('CHARGE DATA')
    print(charge)

    # get amount from charge
    amount = charge.amount

    # get user using chat_id if user not passed in
    if not user:
        # get user using chat_id
        user = User.query({'chatId': chat_id})

    stripeCustomerIds = user['stripeCustomerIds'] if 'stripeCustomerIds' in user else []

    print('Stripe customer IDS')
    print(stripeCustomerIds)

    # TODO: on successful payment, update creator right here
  
    # if customer_id exists
    if len(stripeCustomerIds) > 0:
        print('ATTACHING!')

        try:
            # get payment method id from charge
            payment_method_id = charge['payment_method']

            print('PAYMENT METHOD ID')
            print(payment_method_id)
      
            # attach payment method to stripe customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripeCustomerIds[-1],
            )
        except Exception as e:
            print('Error attaching payment method')
            print(e)  

    print('MODIFYING USER')
    print('AMOUNT: ', amount)

    # update user balance
    new_balance = user['balance'] + amount

    # if total paid not set, set it to 0
    if 'totalPaid' not in user:
        user['totalPaid'] = 0
  
    # increment total paid so far too
    new_total_paid = user['totalPaid'] + amount

    print('new balance: ', new_balance)

    # if user has no stripe customer id, add it
    if user:
        # update user in db
        User.updateWithCustomQuery({'userId': user['userId']}, {
            'balance': new_balance,
            'totalPaid': new_total_paid,
            'stripeCustomerIds': stripeCustomerIds,
            'purchaseEmail': email,
        })
    else:
        # update user in db
        User.updateWithCustomQuery({'chatId': chat_id}, {
            'balance': new_balance,
            'totalPaid': new_total_paid,
            'stripeCustomerIds': stripeCustomerIds,
            'purchaseEmail': email,
        })

    print('updated')
    return True


def charge_customer_automatically(chat_id, amount):
    try:
        # get user
        user = User.query({'chatId': chat_id})

        if not user:
            return False

        if 'stripeCustomerIds' not in user or len(user['stripeCustomerIds']) == 0:
            return False

        # get last stripe customer id
        customer_id = user['stripeCustomerIds'][-1]

        # the invoice item will be on the next invoice
        stripe.InvoiceItem.create(
            customer=customer_id,
            amount=amount,
        )

        # create the next invoice
        stripe.Invoice.create(
            customer=customer_id,
            metadata={'telegram_chat_id': chat_id},
            collection_method="charge_automatically",
        )

        return True
    except Exception as e:
        print('Error charging customer')
        print(e)
        return False

def get_payment_link(amount: int, userData: dict, creatorData: dict, chat_id: str):
    try:
        success_url = os.getenv("STRIPE_SUCCESS_URL")
        cancel_url = os.getenv("STRIPE_CANCEL_URL")

        product_id = stripe.Product.create(name=creatorData['productName'])
        price_id = stripe.Price.create(
            unit_amount= amount * 100,
            currency="usd",
            product=product_id,
        )

        res = stripe.checkout.Session.create(
            success_url = success_url,
            line_items = [
                {
                    "price": price_id.id,
                    "quantity": 1,
                },
            ],
            mode = "payment",
            ui_mode = "hosted",
            metadata = {
                'userId': userData['id'],
                'phone_number': userData['phone_number'],
                'bot_number': creatorData['bot_number'],
                'chatId': chat_id,
                'amount': amount * 100
            }
        )

        print(res)

        link = get_shorten_url(res.url)
        return link
    except Exception as e:
        print("***Error making payment link***")
        print(e)
        return ""
