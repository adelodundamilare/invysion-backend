from typing import Dict, List, Optional
from fastapi import HTTPException, status
from requests import Session
from app.crud.user import user as user_crud
from app.core.security import pwd_context
from app.schemas.auth import UserCreate
from .oauth import OAuthService
from app.services.email import EmailService
import secrets
import string

oauth_service = OAuthService()

class UserService:
    def create_user(self, db, user_data):
        if user_crud.get_by_email(db, email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return user_crud.create(db, obj_in=user_data)

    async def get_or_create_google_user(self, db, token):
        user_data = await oauth_service.verify_google_token(token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        user = user_crud.get_by_email(db, email=user_data["email"])
        if not user:
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(characters) for _ in range(8))

            user = user_crud.create(
                db,
                obj_in=UserCreate(
                    email=user_data["email"],
                    full_name=user_data["name"],
                    auth_provider="google",
                    password=password
                )
            )

            self.update_user(db, user, user_data={
                "verification_code": None,
                "verification_code_expires_at": None,
                "is_verified": True
            })

            EmailService.send_email(
                to_email=user.email,
                subject="Welcome",
                template_name="welcome.html",
                template_context={
                    "name": user.full_name
                }
            )

        return user

    def update_user(self, db, user, user_data):
        return user_crud.update(db, db_obj=user, obj_in=user_data)

    def user_with_email_exists(self, db, email):
        user = user_crud.get_by_email(db, email=email)
        return user is not None

    def find_user_by_email(self, db, email):
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def find_user_by_id(self, db, user_id):
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def change_password(self, db, user, old_password, new_password):
        if not user_crud.authenticate(db, email=user.email, password=old_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        self.update_user(
            db,
            user,
            {"hashed_password": pwd_context.hash(new_password)}
        )

    def get_users(self, db: Session, *, page: int = 1, size: int = 100):
        return user_crud.get_users(db, page=page, size=size)

    def get_recent_signups(self, db: Session, *, limit: int = 10):
        return user_crud.get_recent_signups(db, limit=limit)

    def get_total_users(self, db: Session) -> int:
        return user_crud.get_total_users(db)

    def delete_user(self, db: Session, user_id: int):
        user = user_crud.delete(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user


    def get_many(
        self,
        db: Session,
        page: int = 1,
        size: int = 100,
        filters: Optional[Dict] = None
    ):
        if filters is None:
            filters = {}

        search = filters.get("name")
        user_id = filters.get("user_id")

        return user_crud.get_many(
            db=db,
            page=page,
            size=size,
            search=search,
            user_id=user_id
        )
