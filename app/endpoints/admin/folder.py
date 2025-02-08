from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.utils.deps import is_admin
from app.services import folder as folder_service
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("admin_folder_api", "admin_folder.log")

@router.get("/")
async def get_folders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search folders by name"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        filters = {"name": search, "user_id": user_id}
        return folder_service.get_many(db, page=page, size=size, filters=filters)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/{folder_id}")
def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        folder = folder_service.get_folder(db, folder_id=folder_id)
        return folder
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.delete("/{folder_id}")
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        folder_service.delete_folder(db=db, folder_id=folder_id)
        return {"message": "Folder deleted successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
