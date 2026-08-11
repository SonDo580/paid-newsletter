from sqlmodel import Session as DBSession, select
from typing import Optional

from app.db.models.reader import Reader
from app.db.models.subscription import Subscription


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
