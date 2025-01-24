from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.deps import get_current_user, is_note_owner
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.services import note as note_service
from app.models.user import User
from app.utils.logger import setup_logger

logger = setup_logger("note_api", "note.log")
router = APIRouter()

@router.post("/", response_model=Note)
def create_note(note_in: NoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return note_service.create_note(db=db, user_id=current_user.id, note_in=note_in)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/")
def get_user_notes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return note_service.get_user_notes(db=db, user_id=current_user.id, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.get("/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_note_owner)):
    try:
        return note_service.get_note(db=db, note_id=note_id)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_in: NoteUpdate,
    current_user: User = Depends(is_note_owner),
    db: Session = Depends(get_db)
):
    try:
        return note_service.update_note(db=db, note_id=note_id, note_in=note_in)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

@router.delete("/{note_id}")
def delete_note(note_id: int, current_user: User = Depends(is_note_owner), db: Session = Depends(get_db)):
    try:
        if note_service.delete_note(db=db, note_id=note_id):
            return {"message": "Note deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete note")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

# @router.post("/notes/{note_id}/pin", response_model=Note)
# def toggle_pin_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     note = note_service.get_note(db=db, note_id=note_id)
#     if note is None or note.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Note not found")
#     return note_service.toggle_pin_note(db=db, note_id=note_id)

# @router.post("/notes/{note_id}/archive", response_model=Note)
# def toggle_archive_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     note = note_service.get_note(db=db, note_id=note_id)
#     if note is None or note.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Note not found")
#     return note_service.toggle_archive_note(db=db, note_id=note_id)
