
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class SubscriptionPlan(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    subscription_plan: Optional[str]

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    profession: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    profession: Optional[str] = None
    role: Optional[str] = None
    theme: Optional[str] = None
    avatar: Optional[str] = None
    subscription_plan: SubscriptionPlan
    auth_provider: str
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True