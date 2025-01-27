from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import subscription as subscription_service
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse

router = APIRouter()

@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription_data: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create a new subscription"""
    return subscription_service.create_subscription(
        db=db,
        user_id=subscription_data.user_id,
        price_id=subscription_data.price_id
    )

@router.get("/{user_id}", response_model=SubscriptionResponse)
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    """Get active subscription for a user"""
    subscription = subscription_service.get_subscription(db, user_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    return subscription

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_subscription(subscription_id: str, db: Session = Depends(get_db)):
    """Cancel a subscription"""
    subscription_service.cancel_subscription(db, subscription_id)
    return None
