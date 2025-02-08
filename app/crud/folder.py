from sqlalchemy.orm import Session
from app.models.folder import Folder
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload

def create_folder(db: Session, user_id: int, name: str) -> Folder:
    folder = Folder(user_id=user_id, name=name)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
    return db.query(Folder).filter(Folder.id == folder_id).first()

def get_count(db: Session) -> int:
    return db.query(Folder).count()

def get_user_folders(db: Session, user_id: int) -> List[Folder]:
    return db.query(Folder).filter(Folder.user_id == user_id).all()

def get_user_folder_by_name(db: Session, user_id: int, name: str) -> Optional[Folder]:
    return db.query(Folder).filter(Folder.user_id == user_id).filter(func.lower(Folder.name) == name.lower()).first()

def update_folder(db: Session, folder_id: int, name: str) -> Optional[Folder]:
    folder = get_folder(db, folder_id)
    if folder:
        folder.name = name
        db.commit()
        db.refresh(folder)
    return folder

def delete_folder(db: Session, folder_id: int) -> bool:
    folder = get_folder(db, folder_id)
    if folder:
        db.delete(folder)
        db.commit()
        return True
    return False

def get_many(
    db: Session,
    page: int = 1,
    size: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
) -> dict:
    query = db.query(Folder).options(joinedload(Folder.user))

    if search:
        query = query.filter(Folder.name.ilike(f"%{search}%"))
    if user_id:
        query = query.filter(Folder.user_id == user_id)

    total = query.count()
    pages = (total + size - 1) // size
    offset = (page - 1) * size

    if sort_by:
        sort_column = getattr(Folder, sort_by, None)
        if sort_column:
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

    query = query.offset(offset).limit(size)

    items = query.all()

    folders_with_user_response = []

    for folder in items:
        folder_dict = {
            'id': folder.id,
            'name': folder.name,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at,
            # Add any other Folder attributes you need
        }

        if folder.user:
            folder_dict['user'] = {
                "id":folder.user.id,
                "email":folder.user.email,
                "full_name":folder.user.full_name,
                "avatar":folder.user.avatar,
                # Add other UserResponse fields as needed
            }

        folders_with_user_response.append(folder_dict)

    return {
        'items': folders_with_user_response,
        'total': total,
        'page': page,
        'size': size,
        'pages': pages,
        'has_next': page < pages,
        'has_previous': page > 1
    }
