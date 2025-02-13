from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe

from app.core.config import settings
from app.core.database import get_db
from app.services import subscription as subscription_service
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("note_api", "note.log")

@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription_data: SubscriptionCreate, db: Session = Depends(get_db)):
    try:
        return subscription_service.create_subscription(
            db=db,
            user_id=subscription_data.user_id,
            price_id=subscription_data.price_id
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/{user_id}", response_model=SubscriptionResponse)
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    try:
        subscription = subscription_service.get_subscription(db, user_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        return subscription
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_subscription(subscription_id: str, db: Session = Depends(get_db)):
    try:
        subscription_service.cancel_subscription(db, subscription_id)
        return None
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        # print(settings.STRIPE_WEBHOOK_SECRET, 'settings.STRIPE_WEBHOOK_SECRET')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        subscription_service.handle_webhook_event(db, event)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
