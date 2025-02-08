from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.utils.logger import setup_logger
from app.utils.deps import is_admin
from app.models.user import User
from app.services import plan as plan_service

router = APIRouter()

logger = setup_logger("admin_plan_api", "admin_plan.log")

@router.get("/", response_model=List[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    try:
        return plan_service.list_plans()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/{price_id}", response_model=PlanResponse)
def get_plan(price_id: str, db: Session = Depends(get_db)):
    try:
        plan = plan_service.get_plan(price_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return plan
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(plan_data: PlanCreate,current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    try:
        return plan_service.create_plan(
            name=plan_data.name,
            amount=plan_data.amount,
            interval=plan_data.interval,
            currency=plan_data.currency
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


@router.patch("/{price_id}", response_model=PlanResponse)
def update_plan(price_id: str, plan_data: PlanUpdate, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    try:
        return plan_service.update_plan(price_id, active=plan_data.active)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.delete("/{price_id}")
def delete_plan(price_id: str, current_user: User = Depends(is_admin), db: Session = Depends(get_db)):
    try:
        plan_service.delete_plan(price_id)
        return {"message": "Plan deleted successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
