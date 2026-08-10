from fastapi import APIRouter, Depends

from app.db.connect import DBSessionDep
from app.schemas.auth import CurrentUser
from app.schemas.users import UserProfileResBody
from app.dependencies.auth import get_current_user
from app.services.billing import BillingService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResBody)
def get_me(
    db_session: DBSessionDep, current_user: CurrentUser = Depends(get_current_user)
):
    has_active_subscription = False
    if current_user.reader:
        billing_service = BillingService(db_session)
        active_subscription = billing_service.get_active_subscription(
            current_user.reader
        )
        has_active_subscription = active_subscription is not None
    return UserProfileResBody(
        **current_user.model_dump(),
        has_active_subscription=has_active_subscription,
    )
