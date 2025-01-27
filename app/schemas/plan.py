from pydantic import BaseModel
from typing import Optional

class PlanBase(BaseModel):
    name: str
    amount: int
    interval: str
    currency: str = 'usd'

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    active: bool

class PlanResponse(PlanBase):
    product_id: str
    price_id: str

    class Config:
        orm_mode = True
