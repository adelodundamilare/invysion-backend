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

    def get_recent_signups(self, db: Session, *, limit: int = 10):
        return (
            db.query(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .all()
        )
    def get_total_users(self, db: Session) -> int:
        return db.query(User).count()


    def delete(self, db: Session, *, id: int) -> User:
        obj = db.query(User).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
user = CRUDUser(User)