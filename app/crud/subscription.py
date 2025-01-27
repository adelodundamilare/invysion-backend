from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.subscription import Subscription


def create(db: Session, subscription_data: dict) -> Subscription:
    subscription = Subscription(**subscription_data)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

def get_by_id(db: Session, subscription_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()

def get_by_stripe_id(db: Session, stripe_subscription_id: str) -> Optional[Subscription]:
    return db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()

def get_by_user_id(db: Session, user_id: int) -> List[Subscription]:
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def update(db: Session, subscription_id: int, update_data: dict) -> Optional[Subscription]:
    subscription = get_by_id(db, subscription_id)
    if subscription:
        for key, value in update_data.items():
            setattr(subscription, key, value)
        subscription.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
    return subscription

def update_by_stripe_id(db: Session, stripe_subscription_id: str, update_data: dict) -> Optional[Subscription]:
    subscription = get_by_stripe_id(db, stripe_subscription_id)
    if subscription:
        for key, value in update_data.items():
            setattr(subscription, key, value)
        subscription.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
    return subscription

def delete(db: Session, subscription_id: int) -> bool:
    subscription = get_by_id(db, subscription_id)
    if subscription:
        db.delete(subscription)
        db.commit()
        return True
    return False

def delete_by_stripe_id(db: Session, stripe_subscription_id: str) -> bool:
    subscription = get_by_stripe_id(db, stripe_subscription_id)
    if subscription:
        db.delete(subscription)
        db.commit()
        return True
    return False
