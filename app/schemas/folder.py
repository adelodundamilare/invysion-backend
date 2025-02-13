from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.user import UserResponse

class FolderBase(BaseModel):
    name: str

class FolderCreate(FolderBase):
    pass

class FolderUpdate(FolderBase):
    pass

class Folder(FolderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FolderResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: UserResponse
    items_count: int
    total_size: int  # in bytes

    class Config:
        from_attributes = True
        from_orm = True
