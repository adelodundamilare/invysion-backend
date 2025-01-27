from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    user_id: int
    price_id: str

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    stripe_subscription_id: str
    stripe_customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    canceled_at: Optional[datetime] = None

    class Config:
        orm_mode = True
