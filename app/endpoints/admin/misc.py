from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.user import UserService
from app.utils.deps import is_admin
from app.services import note as note_service
from app.services import payment as payment_service
from app.services import subscription as subscription_service
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("admin_misc_api", "admin_misc.log")
user_service = UserService()

@router.get("/")
async def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    try:
        return {
            "total_users": user_service.get_total_users(db),
            "total_notes": note_service.get_total_notes(db),
            "revenue_generated": await payment_service.get_total_revenue(),
            "active_subscriptions": await subscription_service.get_total_active_subscriptions()
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise