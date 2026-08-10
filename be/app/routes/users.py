from fastapi import APIRouter

from app.schemas.users import UserProfileResBody
from app.dependencies.auth import CurrentUserDep
from app.dependencies.services import SubscriptionsServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResBody)
def get_me(
    current_user: CurrentUserDep, subscriptions_service: SubscriptionsServiceDep
):
    subscription_summary = None
    if current_user.reader:
        subscription_summary = subscriptions_service.get_subscription_summary(
            current_user.reader
        )
    return UserProfileResBody(
        **current_user.model_dump(),
        subscription=subscription_summary,
    )
