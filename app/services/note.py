from typing import List
import tempfile
import os
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import note as note_crud
from app.crud import folder as folder_crud
from app.schemas.note import NoteUpdate
from mutagen import File, MutagenError
from mutagen.mp3 import MP3, HeaderNotFoundError


def create_note(db: Session, user_id: int, note_in):
    folder = folder_crud.get_folder(db, folder_id=note_in['folder_id'])
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    return note_crud.create_note(
        db=db,
        user_id=user_id,
        # **note_in.model_dump(exclude_unset=True)
        **note_in
    )


def get_note(db: Session, note_id: int):
    return note_crud.get_note(db=db, note_id=note_id)


def get_user_notes(db: Session, user_id: int, page: int = 1, per_page: int = 10, skip: int = 0, limit: int = 100):
    notes = note_crud.get_notes_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    total = note_crud.get_total_notes_count(db=db, user_id=user_id)

    return {
        "items": notes,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


def get_folder_notes(db: Session, folder_id: int, skip: int = 0, limit: int = 100) -> List:
    return note_crud.get_notes_by_folder(db=db, folder_id=folder_id, skip=skip, limit=limit)


def update_note(db: Session, note_id: int, note_in: NoteUpdate):
    return note_crud.update_note(db=db, note_id=note_id, note_in=note_in.dict(exclude_unset=True))


def delete_note(db: Session, note_id: int) -> bool:
    return note_crud.delete_note(db=db, note_id=note_id)


def toggle_pin_note(db: Session, note_id: int):
    return note_crud.toggle_pin_note(db=db, note_id=note_id)


def toggle_archive_note(db: Session, note_id: int):
    return note_crud.toggle_archive_note(db=db, note_id=note_id)


def validate_audio_file_and_get_length(file_bytes: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        audio = File(temp_path)

        if audio is None:
            try:
                audio = MP3(temp_path)
            except HeaderNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid MP3 file: Could not find MPEG frame headers"
                )
            except MutagenError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid audio file: {str(e)}"
                )

        if audio is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio file format"
            )

        # Get duration in seconds
        duration = audio.info.length

        max_duration = 600  # 10 minutes
        if duration > max_duration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio file too long. Maximum duration is {max_duration} seconds"
            )

        return duration

    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing audio file: {str(e)}"
            )
        raise e

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)