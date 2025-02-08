from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.utils.logger import setup_logger
from app.utils.deps import is_admin
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.models.user import User
from app.services.user import UserService

router = APIRouter()
user_service = UserService()

logger = setup_logger("admin_user_api", "admin_user.log")

@router.get("/", response_model=List[UserResponse])
def get_users(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        return user_service.get_users(db, page=page, size=size)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user = user_service.find_user_by_id(db, user_id=user_id)
        return user
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/recent/signups", response_model=List[UserResponse])
def get_recent_signups(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        return user_service.get_recent_signups(db=db, limit=limit)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user = user_service.user_with_email_exists(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return user_service.create_user(db=db, user_data=user_in)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user = user_service.find_user_by_id(db, user_id=user_id)
        return user_service.update_user(db=db, user=user, user_data=user_in)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user_service.delete_user(db=db, user_id=user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.put("/{user_id}/suspend-toggle")
def toggle_suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user = user_service.find_user_by_id(db, user_id=user_id)
        data={"is_active": not user.is_active}
        user_service.update_user(db=db, user=user, user_data=data)

        return {"message": "User suspended/un-suspended successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.put("/{user_id}/verify")
def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        user = user_service.find_user_by_id(db, user_id=user_id)
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        data={"is_verified": True}
        user_service.update_user(db=db, user=user, user_data=data)
        return {"message": "User verified successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

