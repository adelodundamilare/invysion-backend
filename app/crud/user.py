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

    def find_by_stripe_id(self, db: Session, id: str) -> Optional[User]:
        return db.query(User).filter(User.stripe_customer_id == id).first()

    def delete(self, db: Session, *, id: int) -> User:
        obj = db.query(User).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_many(
        self,
        db: Session,
        page: int = 1,
        size: int = 100,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc"
    ) -> dict:
        query = db.query(User)

        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        if user_id:
            query = query.filter(User.id == user_id)

        total = query.count()
        pages = (total + size - 1)
        offset = (page - 1) * size

        if sort_by:
            sort_column = getattr(User, sort_by, None)
            if sort_column:
                if sort_order.lower() == 'desc':
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)

        query = query.offset(offset).limit(size)

        items = query.all()

        with_user_response = []

        for item in items:
            item_dict = {
                "id":item.id,
                "email":item.email,
                "full_name":item.full_name,
                "avatar":item.avatar,
                "created_at":item.created_at,
                "updated_at":item.updated_at,
                # Add other UserResponse fields as needed
            }

            with_user_response.append(item_dict)

        return {
            'items': with_user_response,
            'total': total,
            'page': page,
            'size': size,
            'pages': pages,
            'has_next': page < pages,
            'has_previous': page > 1
        }

user = CRUDUser(User)

