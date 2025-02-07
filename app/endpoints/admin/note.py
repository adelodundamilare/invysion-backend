from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.utils.deps import is_admin
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.services import note as note_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/notes", response_model=List[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get all notes (admin only)"""
    notes = note_service.get_folder_notes(db, folder_id=None, skip=skip, limit=limit)
    return notes


@router.get("/notes/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get note by ID (admin only)"""
    note = note_service.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note


@router.post("/notes", response_model=Note)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Create new note (admin only)"""
    return note_service.create_note(db=db, note_in=note_in)


@router.put("/notes/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Update note (admin only)"""
    note = note_service.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note_service.update_note(db=db, note_id=note_id, note_in=note_in)


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Delete note (admin only)"""
    note = note_service.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    note_service.delete_note(db=db, note_id=note_id)
    return {"message": "Note deleted successfully"}
