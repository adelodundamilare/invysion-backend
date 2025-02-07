from sqlalchemy.orm import Session
from app.models.folder import Folder
from typing import List, Optional
from sqlalchemy import func

def create_folder(db: Session, user_id: int, name: str) -> Folder:
    folder = Folder(user_id=user_id, name=name)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
    return db.query(Folder).filter(Folder.id == folder_id).first()

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
