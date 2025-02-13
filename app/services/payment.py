import stripe
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.user import User
from app.schemas.payment import CheckoutSessionCreate, PaymentIntentCreate

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_payment_intent(data: PaymentIntentCreate):
    try:
        price = stripe.Price.retrieve(data.plan_id)

        intent = stripe.PaymentIntent.create(
            amount=price.unit_amount,
            payment_method_types=["card"],
            receipt_email=data.customer_email,
            currency=price.currency
        )
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def confirm_payment_intent(payment_intent_id: str):
    try:
        intent = stripe.PaymentIntent.confirm(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def retrieve_payment_intent(payment_intent_id: str):
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def create_refund(payment_intent_id: str, amount: int = None):
    try:
        refund_params = {"payment_intent": payment_intent_id}
        if amount:
            refund_params["amount"] = amount

        refund = stripe.Refund.create(**refund_params)
        return refund
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_payment_method(payment_method_id: str):
    try:
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        return payment_method
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def attach_payment_method_to_customer(payment_method_id: str, customer_id: str):
    try:
        payment_method = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
        return payment_method
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_total_revenue():
    try:
        params = {"limit": 100}

        total_revenue = 0
        has_more = True
        last_payment = None

        while has_more:
            if last_payment:
                params["starting_after"] = last_payment

            payment_intents = stripe.PaymentIntent.list(**params)

            for payment in payment_intents.data:
                if payment.status == "succeeded":
                    total_revenue += payment.amount

            has_more = payment_intents.has_more
            if has_more and payment_intents.data:
                last_payment = payment_intents.data[-1].id

        return total_revenue
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def list_payments(
    customer_id: str = None,
    limit: int = 100,
    starting_after: str = None,
    ending_before: str = None,
    created_gte: int = None,
    created_lte: int = None,
    status: str = None,
    amount_gte: int = None,
    amount_lte: int = None
):
    try:
        params = {"limit": min(limit, 100)}

        if customer_id:
            params["customer"] = customer_id
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before

        # Add date filters
        if created_gte or created_lte:
            params["created"] = {}
            if created_gte:
                params["created"]["gte"] = created_gte
            if created_lte:
                params["created"]["lte"] = created_lte

        # Add status filter
        if status:
            params["status"] = status

        # Add amount filters
        if amount_gte or amount_lte:
            params["amount"] = {}
            if amount_gte:
                params["amount"]["gte"] = amount_gte
            if amount_lte:
                params["amount"]["lte"] = amount_lte

        payment_intents = stripe.PaymentIntent.list(**params)

        return {
            "data": payment_intents.data,
            "has_more": payment_intents.has_more,
            "total_count": len(payment_intents.data)
        }

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def create_checkout_session(data: CheckoutSessionCreate, user: User):
    try:
        session_params = {
            "line_items": [{"price": data.plan_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": data.success_url,
            "cancel_url": data.cancel_url,
            "customer_email": user.email
        }

        checkout_session = stripe.checkout.Session.create(**session_params)

        return {
            "id": checkout_session.id,
            "url": checkout_session.url
        }

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
