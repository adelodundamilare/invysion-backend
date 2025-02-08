from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.utils.deps import is_admin
from app.services import note as note_service
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("admin_note_api", "admin_note.log")

@router.get("/")
async def get_notes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search notes by title"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        filters = {"title": search, "user_id": user_id}
        return note_service.get_many(db, page=page, size=size, filters=filters)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        note = note_service.get_note(db, note_id=note_id)
        return note
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        note_service.delete_note(db=db, note_id=note_id)
        return {"message": "Note deleted successfully"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
