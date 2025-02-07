from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase, PaginatedResponse
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import pwd_context

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        create_data = obj_in.dict()
        create_data.pop("password")
        db_obj = User(
            **create_data,
            hashed_password=pwd_context.hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def get_users(self, db: Session, *, page: int = 1, size: int = 100):
        return db.query(User).offset(page).limit(size).all()

        # if page < 1:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Page number must be greater than 0"
        #     )

        # if size < 1:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Page size must be greater than 0"
        #     )

        # offset = (page - 1) * size
        # total = db.query(User).count()
        # items = (
        #     db.query(User)
        #     .order_by(User.created_at.desc())
        #     .offset(offset)
        #     .limit(size)
        #     .all()
        # )
        # pages = (total + size - 1)

        # if total > 0 and page > pages:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Page number {page} exceeds total pages {pages}"
        #     )

        # return PaginatedResponse(
        #     items=items,
        #     total=total,
        #     page=page,
        #     size=size,
        #     pages=pages,
        #     has_next=page < pages,
        #     has_previous=page > 1
        # )

    def delete(self, db: Session, *, id: int) -> User:
        obj = db.query(User).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
user = CRUDUser(User)