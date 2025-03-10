from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    # is_pinned: bool = False
    # is_archived: bool = False
    # color: Optional[str] = None


class NoteCreate(NoteBase):
    folder_id: Optional[int]
    title: Optional[str]


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    # is_pinned: Optional[bool] = None
    # is_archived: Optional[bool] = None
    # color: Optional[str] = None
    # folder_id: Optional[int] = None


class Note(NoteBase):
    id: int
    user_id: int
    folder_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
