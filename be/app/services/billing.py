import stripe
from sqlmodel import Session as DBSession
from fastapi import HTTPException, status
from loguru import logger

from app.db.models.reader import Reader
from app.schemas.payments import CreatePortalSessionReqBody
from app.utils.url import fe_url_builder


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
