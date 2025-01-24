
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import folder as folder_schema
from app.utils.logger import setup_logger
from app.services import folder as folder_service
from app.utils.deps import get_current_user
from app.models.user import User

logger = setup_logger("folder_api", "folder.log")

router = APIRouter()


@router.post("/")
async def create_folder(folder_data: folder_schema.FolderCreate,
                       current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    try:
        folder = folder_service.create_folder(db, folder_data=folder_data, user_id=current_user.id)
        return folder
    except Exception as e:
        logger.error(f"Folder creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/")
async def get_folders(current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    try:
        folders = folder_service.get_user_folders(db, user_id=current_user.id)
        return folders
    except Exception as e:
        logger.error(f"Getting folders failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{folder_id}")
async def get_folder(folder_id: int,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    try:
        folder = folder_service.get_folder(db, folder_id=folder_id, user_id=current_user.id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        return folder
    except Exception as e:
        logger.error(f"Getting folder failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{folder_id}")
async def update_folder(folder_id: int,
                       folder_data: folder_schema.FolderUpdate,
                       current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    try:
        folder = folder_service.update_folder(db, folder_id=folder_id, folder_data=folder_data, user_id=current_user.id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        return folder
    except Exception as e:
        logger.error(f"Updating folder failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: int,
                       current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    try:
        deleted = folder_service.delete_folder(db, folder_id=folder_id, user_id=current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        return None
    except Exception as e:
        logger.error(f"Deleting folder failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
