from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import folder as folder_crud
from app.schemas import folder as folder_schema
from typing import List

def create_folder(db: Session, user_id: int, folder_data: folder_schema.FolderCreate) -> folder_schema.Folder:
    try:
        return folder_crud.create_folder(db, user_id=user_id, name=folder_data.name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create folder: {str(e)}"
        )

def get_folder(db: Session, folder_id: int) -> folder_schema.Folder:
    folder = folder_crud.get_folder(db, folder_id=folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    return folder

def get_user_folders(db: Session, user_id: int) -> List[folder_schema.Folder]:
    return folder_crud.get_user_folders(db, user_id=user_id)

def update_folder(db: Session, folder_id: int, folder_data: folder_schema.FolderUpdate) -> folder_schema.Folder:
    folder = folder_crud.update_folder(db, folder_id=folder_id, name=folder_data.name)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    return folder

def delete_folder(db: Session, folder_id: int) -> bool:
    if not folder_crud.delete_folder(db, folder_id=folder_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    return True

def get_or_create_uncategorized_folder(db: Session, user_id: int) -> int:
    try:
        folder = folder_crud.get_user_folder_by_name(
            db=db,
            user_id=user_id,
            name="Uncategorized"
        )

        if folder:
            return folder.id

        # If not found, create it
        folder_data = folder_schema.FolderCreate(name="Uncategorized")
        new_folder = folder_crud.create_folder(
            db=db,
            user_id=user_id,
            name=folder_data.name
        )
        return new_folder.id

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not get or create uncategorized folder: {str(e)}"
        )