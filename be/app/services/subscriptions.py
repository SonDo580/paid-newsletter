from sqlmodel import Session as DBSession, select
from typing import Optional

from app.db.models.reader import Reader
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.schemas.users import SubscriptionSummary


class SubscriptionsService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    def get_latest_subscription(self, reader: Reader) -> Optional[Subscription]:
        if not reader.stripe_customer_id:
            return None

        return self.db_session.exec(
            select(Subscription)
            .where(
                Subscription.reader_id == reader.id,
            )
            .order_by(Subscription.created_at.desc())
        ).first()

    def get_subscription_summary(self, reader: Reader) -> Optional[SubscriptionSummary]:
        latest_subscription = self.get_latest_subscription(reader)
        if not latest_subscription or latest_subscription.status not in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        ]:
            return None

        return SubscriptionSummary(
            current_period_start=latest_subscription.current_period_start,
            current_period_end=latest_subscription.current_period_end,
            cancel_at_period_end=latest_subscription.cancel_at_period_end,
            is_active=latest_subscription.status == SubscriptionStatus.ACTIVE,
            is_past_due=latest_subscription.status == SubscriptionStatus.PAST_DUE,
        )
