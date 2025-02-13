from pydantic import BaseModel, EmailStr
from typing import Optional

class PaymentIntentCreate(BaseModel):
    plan_id: str
    customer_email: Optional[str] = None
    payment_method_id: Optional[str] = None
    setup_future_usage: Optional[str] = None

class CheckoutSessionCreate(BaseModel):
    plan_id: str
    success_url:str
    cancel_url:str
    # payment_method_id: Optional[str] = None
    # setup_future_usage: Optional[str] = None

class PaymentMethodCreate(BaseModel):
    payment_method_id: str
    customer_id: str

class RefundCreate(BaseModel):
    payment_intent_id: str
    amount: Optional[int] = None

class PaymentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    client_secret: Optional[str] = None

    class Config:
        from_attributes = True
