from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
        orm_mode = True
