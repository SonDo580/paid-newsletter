import stripe
from sqlmodel import Session as DBSession, select, update
from fastapi import HTTPException, status
from loguru import logger

from app.config.settings import settings
from app.db.models.reader import Reader
from app.db.models.article import Article
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.db.models.entitlement import Entitlement
from app.schemas.payments import (
    PurchaseCheckoutReqBody,
    PurchaseCheckoutMetadata,
    SubscriptionCheckoutReqBody,
    SubscriptionCheckoutMetadata,
    SubscriptionMetadata,
)
from app.utils.url import fe_url_builder


class CheckoutService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    def create_purchase_checkout(
        self, reader: Reader, payload: PurchaseCheckoutReqBody
    ) -> str:
        """Return checkout URL."""
        # Verify that article exists
        article_id = payload.article_id
        article = self.db_session.get(Article, article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        # Check if reader already owns article
        existing_entitlement = self.db_session.exec(
            select(Entitlement).where(
                Entitlement.reader_id == reader.id,
                Entitlement.article_id == article_id,
            )
        ).first()
        if existing_entitlement:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already own this article",
            )

        # Get or create Stripe customer ID for reader
        stripe_customer_id = self.__get_or_create_stripe_customer(reader)

        try:
            # Record PENDING payment
            payment = Payment(
                reader_id=reader.id,
                amount_cents=0,  # populate on successful payment,
                currency=settings.CURRENCY,
                status=PaymentStatus.PENDING,
            )
            self.db_session.add(payment)

            # Generate payment.id without committing transaction yet
            self.db_session.flush()

            # Create Stripe checkout session
            redirect_url = fe_url_builder.build(payload.redirect_path)
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": settings.CURRENCY,
                            "unit_amount": settings.ARTICLE_FEE_CENTS,
                            "product_data": {"name": article.title},
                        },
                        "quantity": 1,
                    }
                ],
                metadata=PurchaseCheckoutMetadata(
                    checkout_type="purchase",
                    payment_id=payment.id,
                    article_id=article_id,
                    reader_id=reader.id,
                ).to_stripe_metadata(),
                success_url=redirect_url,
                cancel_url=redirect_url,
            )

            self.db_session.commit()
            return checkout_session.url
        except Exception as e:
            logger.exception(
                f"Error creating purchase checkout session for reader {reader.id}: {e}"
            )
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create purchase checkout session",
            )

    def create_subscription_checkout(
        self, reader: Reader, payload: SubscriptionCheckoutReqBody
    ) -> str:
        """Return checkout URL."""
        # Check for existing active subscription
        active_subscription = self.db_session.exec(
            select(Subscription).where(
                Subscription.reader_id == reader.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        ).first()
        if active_subscription:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an active subscription",
            )

        # Get or create Stripe customer ID for reader
        stripe_customer_id = self.__get_or_create_stripe_customer(reader)

        try:
            # Record PENDING payment
            payment = Payment(
                reader_id=reader.id,
                amount_cents=0,  # populate on successful payment
                currency=settings.CURRENCY,
                status=PaymentStatus.PENDING,
            )
            self.db_session.add(payment)

            # Generate payment.id without committing transaction yet
            self.db_session.flush()

            # Create Stripe checkout session
            redirect_url = fe_url_builder.build(payload.redirect_path)
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                mode="subscription",
                line_items=[
                    {
                        "price": settings.STRIPE_SUBSCRIPTION_PRICE_ID,
                        "quantity": 1,
                    }
                ],
                metadata=SubscriptionCheckoutMetadata(
                    checkout_type="subscription",
                    payment_id=payment.id,
                    reader_id=reader.id,
                ).to_stripe_metadata(),
                subscription_data={
                    "metadata": SubscriptionMetadata(
                        reader_id=reader.id
                    ).to_stripe_metadata()
                },
                success_url=redirect_url,
                cancel_url=redirect_url,
            )

            self.db_session.commit()
            return checkout_session.url
        except Exception as e:
            logger.exception(
                f"Error creating subscription checkout session for reader {reader.id}: {e}"
            )
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create subscription checkout session",
            )

    def __get_or_create_stripe_customer(self, reader: Reader) -> str:
        """Return Stripe customer ID of reader."""
        if reader.stripe_customer_id:
            return reader.stripe_customer_id

        # Create Stripe customer
        try:
            customer = stripe.Customer.create(
                email=reader.email, metadata={"reader_id": str(reader.id)}
            )
        except stripe.error.StripeError as e:
            logger.exception(
                f"Failed to create Stripe customer for reader {reader.id}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PSP error"
            )

        # Only update if stripe_customer_id is still NULL
        try:
            stmt = (
                update(Reader)
                .where(Reader.id == reader.id)
                .where(Reader.stripe_customer_id.is_(None))
                .values(stripe_customer_id=customer.id)
            )
            result = self.db_session.exec(stmt)
            self.db_session.commit()
        except Exception as e:
            logger.exception(
                f"Error updating Stripe customer ID for reader {reader.id}: {e}"
            )
            self.__safe_delete_orphaned_stripe_customer(customer.id)
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DB error",
            )

        if result.rowcount == 1:
            # Current thread committed Stripe customer ID successfully
            reader.stripe_customer_id = customer.id
        else:
            # Another thread committed Stripe customer ID before current thread
            self.__safe_delete_orphaned_stripe_customer(customer.id)
            try:
                self.db_session.refresh(reader)
            except Exception as e:
                logger.exception(f"Failed to refresh reader {reader.id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="DB error",
                )

        return reader.stripe_customer_id

    def __safe_delete_orphaned_stripe_customer(self, customer_id: str) -> None:
        """Delete orphaned Stripe customer. Don't fail on error."""
        try:
            stripe.Customer.delete(customer_id)
        except stripe.error.StripeError as e:
            logger.warning(
                f"Failed to delete orphaned Stripe customer {customer_id}: {e}"
            )
