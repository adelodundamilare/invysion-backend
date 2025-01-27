from pydantic import BaseModel
from typing import Optional

class PaymentIntentCreate(BaseModel):
    amount: int
    currency: str = 'usd'
    payment_method_id: Optional[str] = None
    customer_id: Optional[str] = None
    setup_future_usage: Optional[str] = None

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
        orm_mode = True
