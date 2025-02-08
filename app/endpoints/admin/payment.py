from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.logger import setup_logger
from app.utils.deps import is_admin
from app.models.user import User
from app.services import payment as payment_service

router = APIRouter()

logger = setup_logger("admin_payment_api", "admin_payment.log")

@router.get("/", response_model=dict)
async def list_payments(
    customer_id: Optional[str] = None,
    limit: int = 100,
    starting_after: Optional[str] = None,
    ending_before: Optional[str] = None,
    created_gte: Optional[int] = None,
    created_lte: Optional[int] = None,
    status: Optional[str] = None,
    amount_gte: Optional[int] = None,
    amount_lte: Optional[int] = None,
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.list_payments(
            customer_id=customer_id,
            limit=limit,
            starting_after=starting_after,
            ending_before=ending_before,
            created_gte=created_gte,
            created_lte=created_lte,
            status=status,
            amount_gte=amount_gte,
            amount_lte=amount_lte
        )
    except Exception as e:
        logger.error(f"Error listing payments: {str(e)}")
        raise

@router.get("/{payment_intent_id}")
async def get_payment(
    payment_intent_id: str,
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.retrieve_payment_intent(payment_intent_id)
    except Exception as e:
        logger.error(f"Error retrieving payment {payment_intent_id}: {str(e)}")
        raise

@router.post("/{payment_intent_id}/refund")
async def refund_payment(
    payment_intent_id: str,
    amount: Optional[int] = None,
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.create_refund(payment_intent_id, amount)
    except Exception as e:
        logger.error(f"Error refunding payment {payment_intent_id}: {str(e)}")
        raise
