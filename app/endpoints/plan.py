from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.services import plan as plan_service
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.utils.deps import is_admin

router = APIRouter()

@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(plan_data: PlanCreate,current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    """Create a new subscription plan"""
    return plan_service.create_plan(
        name=plan_data.name,
        amount=plan_data.amount,
        interval=plan_data.interval,
        currency=plan_data.currency
    )

@router.get("/{price_id}", response_model=PlanResponse)
def get_plan(price_id: str, db: Session = Depends(get_db)):
    """Get details of a specific plan"""
    plan = plan_service.get_plan(price_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@router.get("/", response_model=List[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    """List all available plans"""
    return plan_service.list_plans()

@router.patch("/{price_id}", response_model=PlanResponse)
def update_plan(price_id: str, plan_data: PlanUpdate, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    """Update a plan's status"""
    return plan_service.update_plan(price_id, active=plan_data.active)

@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(price_id: str, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    """Delete (deactivate) a plan"""
    plan_service.delete_plan(price_id)
    return None
