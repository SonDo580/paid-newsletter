import stripe
from sqlmodel import Session as DBSession, select
from fastapi import HTTPException, status
from loguru import logger
from typing import Optional

from app.db.models.reader import Reader
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.schemas.payments import CreatePortalSessionReqBody
from app.utils.url import fe_url_builder
from app.utils.datetime import datetime_utils


class BillingService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    def create_portal_session(
        self, reader: Reader, payload: CreatePortalSessionReqBody
    ) -> str:
        """Return billing portal URL."""
        if not reader.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No billing history found for this account",
            )

        try:
            return_url = fe_url_builder.build(payload.redirect_path)
            portal_session = stripe.billing_portal.Session.create(
                customer=reader.stripe_customer_id, return_url=return_url
            )
            return portal_session.url
        except stripe.error.StripeError as e:
            logger.exception(
                f"Failed to create billing portal session for reader {reader.id}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create billing portal session",
            )

    def get_active_subscription(self, reader: Reader) -> Optional[Subscription]:
        if not reader.stripe_customer_id:
            return None

        now = datetime_utils.now_utc()
        active_subscription = self.db_session.exec(
            select(Subscription).where(
                Subscription.reader_id == reader.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end > now,
            )
        ).first()
        return active_subscription
