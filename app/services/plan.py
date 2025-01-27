from typing import List, Optional
from fastapi import HTTPException, status
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_plan(name: str, amount: int, interval: str, currency: str = 'usd') -> dict:
    """Create a new plan in Stripe"""
    try:
        product = stripe.Product.create(name=name)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount,
            currency=currency,
            recurring={"interval": interval}
        )
        return {
            "product_id": product.id,
            "price_id": price.id,
            "name": name,
            "amount": amount,
            "currency": currency,
            "interval": interval
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def get_plan(price_id: str) -> Optional[dict]:
    """Get plan details from Stripe"""
    try:
        price = stripe.Price.retrieve(price_id)
        product = stripe.Product.retrieve(price.product)
        return {
            "product_id": product.id,
            "price_id": price.id,
            "name": product.name,
            "amount": price.unit_amount,
            "currency": price.currency,
            "interval": price.recurring.interval
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def list_plans() -> List[dict]:
    """List all active plans"""
    try:
        prices = stripe.Price.list(active=True)
        plans = []
        for price in prices:
            product = stripe.Product.retrieve(price.product)
            plans.append({
                "product_id": product.id,
                "price_id": price.id,
                "name": product.name,
                "amount": price.unit_amount,
                "currency": price.currency,
                "interval": price.recurring.interval
            })
        return plans
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def update_plan(price_id: str, active: bool = True) -> dict:
    """Update plan status in Stripe"""
    try:
        price = stripe.Price.modify(
            price_id,
            active=active
        )
        product = stripe.Product.retrieve(price.product)
        return {
            "product_id": product.id,
            "price_id": price.id,
            "name": product.name,
            "amount": price.unit_amount,
            "currency": price.currency,
            "interval": price.recurring.interval,
            "active": price.active
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def delete_plan(price_id: str) -> bool:
    """Delete a plan in Stripe (deactivate)"""
    try:
        price = stripe.Price.modify(
            price_id,
            active=False
        )
        return True
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
