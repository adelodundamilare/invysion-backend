from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.logger import setup_logger
from app.utils.deps import is_admin
from app.models.user import User
from app.services import subscription as subscription_service

router = APIRouter()

logger = setup_logger("admin_subscription_api", "admin_subscription.log")

@router.get("/active", response_model=dict)
async def list_subscriptions(
    limit: int = 100,
    starting_after: str = None,
    ending_before: str = None,
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    try:
        return await subscription_service.list_active_subscriptions(
            limit=limit,
            starting_after=starting_after,
            ending_before=ending_before
        )
    except Exception as e:
        logger.error(f"Error listing subscriptions: {str(e)}")
        raise
