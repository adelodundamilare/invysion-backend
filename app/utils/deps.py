
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.crud.user import user as user_crud
from app.crud import folder as folder_crud
from app.crud import note as note_crud
from app.models.user import User

http_bearer = HTTPBearer()

async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def is_folder_owner(
    folder_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    folder = folder_crud.get_folder(db, folder_id=folder_id)
    if not folder or folder.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this folder"
        )
    return folder

def is_note_owner(
    note_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = note_crud.get_note(db, note_id=note_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this Note"
        )
    return note