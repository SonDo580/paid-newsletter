from fastapi import APIRouter
from typing import Optional

from app.schemas.subscriptions import SubscriptionSummary
from app.dependencies.auth import CurrentUserDep
from app.dependencies.services import SubscriptionsServiceDep

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/me", response_model=Optional[SubscriptionSummary])
def get_my_subscription(
    current_user: CurrentUserDep, subscriptions_service: SubscriptionsServiceDep
):
    if not current_user.reader:
        return None
    latest_subscription = subscriptions_service.get_latest_subscription(
        current_user.reader
    )
    if not latest_subscription:
        return None
    return SubscriptionSummary(**latest_subscription.model_dump(exclude_none=True))
