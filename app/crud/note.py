from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.note import Note
from fastapi.encoders import jsonable_encoder

def create_note(
    db: Session,
    user_id: int,
    folder_id: int,
    title: str,
    **kwargs) -> Note:
    note = Note(
        user_id=user_id,
        folder_id=folder_id,
        title=title,
        **kwargs
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_note(db: Session, note_id: int) -> Optional[Note]:
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    return db.query(Note).filter(Note.user_id == user_id).offset(skip).limit(limit).all()

def get_notes_by_folder(db: Session, folder_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    return db.query(Note).filter(Note.folder_id == folder_id).offset(skip).limit(limit).all()

def get_total_notes_count(db: Session, user_id: int) -> int:
    return db.query(Note).filter(Note.user_id == user_id).count()

def update_note(db: Session, note_id: int, note_in: dict) -> Optional[Note]:
    db_note = get_note(db, note_id)
    if not db_note:
        return None

    obj_data = jsonable_encoder(db_note)
    for field in obj_data:
        if field in note_in:
            setattr(db_note, field, note_in[field])

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> bool:
    note = get_note(db, note_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True

def toggle_pin_note(db: Session, note_id: int) -> Optional[Note]:
    note = get_note(db, note_id)
    if not note:
        return None
    note.is_pinned = not note.is_pinned
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def toggle_archive_note(db: Session, note_id: int) -> Optional[Note]:
    note = get_note(db, note_id)
    if not note:
        return None
    note.is_archived = not note.is_archived
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
