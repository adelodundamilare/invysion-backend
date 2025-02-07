from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.utils.deps import is_admin
from app.schemas.folder import Folder, FolderCreate, FolderUpdate
from app.services import folder as folder_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/folders", response_model=List[Folder])
def get_folders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get all folders (admin only)"""
    folders = folder_service.get_folders(db, skip=skip, limit=limit)
    return folders


@router.get("/folders/{folder_id}", response_model=Folder)
def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Get folder by ID (admin only)"""
    folder = folder_service.get_folder(db, folder_id=folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    return folder


@router.post("/folders", response_model=Folder)
def create_folder(
    folder_in: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Create new folder (admin only)"""
    return folder_service.create_folder(db=db, folder_in=folder_in)


@router.put("/folders/{folder_id}", response_model=Folder)
def update_folder(
    folder_id: int,
    folder_in: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Update folder (admin only)"""
    folder = folder_service.get_folder(db, folder_id=folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    return folder_service.update_folder(db=db, folder=folder, folder_in=folder_in)


@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Delete folder (admin only)"""
    folder = folder_service.get_folder(db, folder_id=folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    folder_service.delete_folder(db=db, folder_id=folder_id)
    return {"message": "Folder deleted successfully"}
