from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import payment as payment_service
from app.schemas.payment import CheckoutSessionCreate, PaymentIntentCreate, PaymentMethodCreate, RefundCreate, PaymentResponse
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/create-payment-intent", response_model=PaymentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        payment_intent = await payment_service.create_payment_intent(data=payment_data)

        return PaymentResponse(
            id=payment_intent.id,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            status=payment_intent.status,
            client_secret=payment_intent.client_secret
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/create-checkout-session", response_model=dict)
async def create_checkout_session(
    payment_data: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        checkout_session = await payment_service.create_checkout_session(data=payment_data, user=current_user)
        return {
            "id": checkout_session["id"],
            "url": checkout_session["url"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/attach-payment-method")
async def attach_payment_method(
    payment_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.attach_payment_method_to_customer(
            payment_method_id=payment_data.payment_method_id,
            customer_id=payment_data.customer_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refund", response_model=dict)
async def create_refund(
    refund_data: RefundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.create_refund(
            payment_intent_id=refund_data.payment_intent_id,
            amount=refund_data.amount
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/payment-intent/{payment_intent_id}")
async def get_payment_intent(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return await payment_service.retrieve_payment_intent(payment_intent_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
