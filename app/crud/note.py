from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.note import Note
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload

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

def get_total_notes_count(db: Session) -> int:
    return db.query(Note).count()

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

def get_total_notes(db: Session) -> int:
    return db.query(Note).count()


def get_many(
    db: Session,
    page: int = 1,
    size: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
) -> dict:
    query = db.query(Note).options(joinedload(Note.user))

    if search:
        query = query.filter(Note.title.ilike(f"%{search}%"))
    if user_id:
        query = query.filter(Note.user_id == user_id)

    total = query.count()
    pages = (total + size - 1) // size
    offset = (page - 1) * size

    if sort_by:
        sort_column = getattr(Note, sort_by, None)
        if sort_column:
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

    query = query.offset(offset).limit(size)

    items = query.all()

    with_user_response = []

    for item in items:
        item_dict = {
            'id': item.id,
            'title': item.title,
            'created_at': item.created_at,
            'updated_at': item.updated_at,
            # Add any other Folder attributes you need
        }

        if item.user:
            item_dict['user'] = {
                "id":item.user.id,
                "email":item.user.email,
                "full_name":item.user.full_name,
                "avatar":item.user.avatar,
                # Add other UserResponse fields as needed
            }

        with_user_response.append(item_dict)

    return {
        'items': with_user_response,
        'total': total,
        'page': page,
        'size': size,
        'pages': pages,
        'has_next': page < pages,
        'has_previous': page > 1
    }
