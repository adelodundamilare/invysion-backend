from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
import stripe
from app.core.config import settings
from app.models.subscription import Subscription
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user import UserService

user_service = UserService()

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_subscription(self, db: Session, user_id: int, price_id: str) -> Subscription:
    try:
        # Get or create stripe customer
        customer = _get_or_create_customer(db, user_id)

        # Create subscription in Stripe
        stripe_subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )

        # Create subscription record in database
        subscription = Subscription(
            user_id=user_id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=customer.id,
            status=stripe_subscription.status,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end)
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        return subscription

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def cancel_subscription(self, db: Session, subscription_id: str) -> None:
    try:
        # Cancel subscription in Stripe
        stripe.Subscription.delete(subscription_id)

        # Update subscription status in database
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = 'canceled'
            subscription.canceled_at = datetime.utcnow()
            db.commit()

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def get_subscription(self, db: Session, user_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_(['active', 'trialing'])
    ).first()

def _get_or_create_customer(self, db: Session, user_id: int):
    # Get user details from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user already has stripe customer id
    if user.stripe_customer_id:
        return stripe.Customer.retrieve(user.stripe_customer_id)

    # Create new stripe customer
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name
    )

    # Update user with stripe customer id
    user.stripe_customer_id = customer.id
    db.commit()

    return customer

async def get_total_active_subscriptions():
    try:
        params = {"limit": 100, "status": "active"}
        total_subscriptions = 0
        has_more = True
        last_subscription = None

        while has_more:
            if last_subscription:
                params["starting_after"] = last_subscription

            subscriptions = stripe.Subscription.list(**params)
            total_subscriptions += len(subscriptions.data)

            has_more = subscriptions.has_more
            if has_more and subscriptions.data:
                last_subscription = subscriptions.data[-1].id

        return total_subscriptions

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def list_active_subscriptions(
    limit: int = 100,
    starting_after: str = None,
    ending_before: str = None
) -> dict:
    try:
        params = {
            "limit": min(limit, 100),
            "status": "active"
        }

        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before

        subscriptions = stripe.Subscription.list(**params)

        return {
            "data": subscriptions.data,
            "has_more": subscriptions.has_more,
            "total_count": len(subscriptions.data)
        }

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def handle_webhook_event(db, event):
    try:
        if event.type == 'customer.subscription.created':
            _handle_subscription_created(db, event.data.object)
        if event.type == 'customer.subscription.updated':
            _handle_subscription_updated(db, event.data.object)
        elif event.type == 'customer.subscription.deleted':
            _handle_subscription_deleted(event.data.object)
        elif event.type == 'invoice.payment_succeeded':
            _handle_payment_succeeded(event.data.object)
        elif event.type == 'invoice.payment_failed':
            _handle_payment_failed(event.data.object)
        elif event.type == 'customer.created':
            _handle_customer_created(db, event.data.object)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def _handle_subscription_created(db, subscription_object):
    plan_id = subscription_object.get('plan').get('id')
    user = user_service.find_user_by_stripe_id(db, id=subscription_object.get('customer'))
    user_service.update_user(db, user, user_data={"subscription_plan": plan_id})

    # todo, send an email
    pass

def _handle_customer_created(db, subscription_object):
    customer_email = subscription_object.email
    customer_id = subscription_object.id

    user = user_service.find_user_by_email(db, email=customer_email)
    user_service.update_user(db, user, user_data={"stripe_customer_id": customer_id})

    print('stripe customer id updated', customer_id)
    pass

def _handle_subscription_updated(db, subscription_object):
    print(subscription_object, 'subscription_object')
    user = user_service.find_user_by_stripe_id(db, id=subscription_object.customer)
    # user_service.update_user(db, user, user_data={"stripe_customer_id": customer_id})
    print('stripe subscription id updated')
    # todo, send an email
    pass

def _handle_subscription_deleted(subscription_object):
    print('calling... _handle_subscription_deleted')
    # send email
    pass

def _handle_payment_succeeded(invoice_object):
    print('calling... _handle_payment_succeeded')
    # user data
    # send email, update
    # record transaction...
    pass

def _handle_payment_failed(invoice_object):
    print('calling... _handle_payment_failed')
    # send email
    pass
