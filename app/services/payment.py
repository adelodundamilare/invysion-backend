import stripe
from fastapi import HTTPException, status
from app.core.config import settings

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_payment_intent(amount: int, currency: str = "usd"):
    """Create a payment intent"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency
        )
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def confirm_payment_intent(payment_intent_id: str):
    """Confirm a payment intent"""
    try:
        intent = stripe.PaymentIntent.confirm(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def retrieve_payment_intent(payment_intent_id: str):
    """Retrieve a payment intent"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def create_refund(payment_intent_id: str, amount: int = None):
    """Create a refund for a payment"""
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
    """Retrieve a payment method"""
    try:
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        return payment_method
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def attach_payment_method_to_customer(payment_method_id: str, customer_id: str):
    """Attach a payment method to a customer"""
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
