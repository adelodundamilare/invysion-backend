from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.services import plan as plan_service
from app.schemas.plan import PlanResponse, PlanUpdate
from app.utils.deps import is_admin

router = APIRouter()

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
