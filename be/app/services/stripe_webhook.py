import stripe
from fastapi import Request, HTTPException, status
import json
from sqlmodel import Session as DBSession, select
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app.config.settings import settings
from app.common.constants import Env
from app.db.models.entitlement import Entitlement, EntitlementSource
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.schemas.payments import (
    CheckoutMetadata,
    PurchaseCheckoutMetadata,
    SubscriptionCheckoutMetadata,
    SubscriptionMetadata,
)
from app.utils.datetime import datetime_utils


class StripeWebhookService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    async def verify_request(self, request: Request) -> stripe.Event:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if settings.ENV == Env.LOCAL:
            event_dict = json.loads(payload)
            return stripe.Event.construct_from(event_dict, settings.STRIPE_SECRET_KEY)
        else:
            try:
                return stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
                )
            except stripe.error.SignatureVerificationError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
                )

    def handle_event(self, event: stripe.Event) -> None:
        data_object = event.data.object
        match event.type:
            case "checkout.session.completed":
                self.__handle_checkout_session_completed(data_object)
            case "customer.subscription.updated" | "customer.subscription.deleted":
                self.__handle_subscription_updated_or_deleted(data_object)
            case "invoice.payment_succeeded":
                self.__handle_invoice_payment_succeeded(data_object)
            case _:
                pass  # Ignore other event types

    def __handle_checkout_session_completed(
        self, checkout_session: stripe.checkout.Session
    ) -> None:
        meta_dict = checkout_session.metadata
        meta = CheckoutMetadata.model_validate(meta_dict)
        checkout_type = meta.checkout_type
        if checkout_type == "purchase":
            meta = PurchaseCheckoutMetadata.model_validate(meta_dict)
            self.__fulfill_purchase_checkout(checkout_session, meta)
        elif checkout_type == "subscription":
            meta = SubscriptionCheckoutMetadata.model_validate(meta_dict)
            self.__fulfill_subscription_checkout(checkout_session, meta)

    def __fulfill_purchase_checkout(
        self,
        checkout_session: stripe.checkout.Session,
        meta: PurchaseCheckoutMetadata,
    ) -> None:
        payment_id = meta.payment_id
        article_id = meta.article_id
        reader_id = meta.reader_id

        payment = self.db_session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} not found in DB",
            )
        if payment.status == PaymentStatus.SUCCEEDED:  # race condition
            return

        payment.status = PaymentStatus.SUCCEEDED
        payment.stripe_payment_intent_id = checkout_session.payment_intent
        payment.amount_cents = checkout_session.amount_total

        existing_entitlement = self.db_session.exec(
            select(Entitlement).where(
                Entitlement.reader_id == reader_id,
                Entitlement.article_id == article_id,
            )
        ).first()

        if not existing_entitlement:
            entitlement = Entitlement(
                reader_id=reader_id,
                article_id=article_id,
                payment_id=payment_id,
                source=EntitlementSource.PURCHASE,
            )
            self.db_session.add(entitlement)

        try:
            self.db_session.commit()
        except IntegrityError:  # race condition
            self.db_session.rollback()
        except Exception as e:
            self.db_session.rollback()
            err_msg = f"Failed to fulfill purchase for payment {payment_id}: {e}"
            logger.exception(err_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err_msg,
            )

    def __fulfill_subscription_checkout(
        self,
        checkout_session: stripe.checkout.Session,
        meta: SubscriptionCheckoutMetadata,
    ) -> None:
        payment_id = meta.payment_id
        reader_id = meta.reader_id

        payment = self.db_session.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} not found in DB",
            )
        if payment.status == PaymentStatus.SUCCEEDED:  # race condition
            return

        payment.status = PaymentStatus.SUCCEEDED
        payment.stripe_invoice_id = checkout_session.invoice
        payment.stripe_payment_intent_id = checkout_session.payment_intent
        payment.amount_cents = checkout_session.amount_total

        stripe_subscription_id = checkout_session.subscription
        stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        existing_subscription = self.db_session.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        ).first()

        if not existing_subscription:
            subscription_item = stripe_subscription.items.data[0]
            subscription = Subscription(
                reader_id=reader_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_price_id=subscription_item.price.id,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime_utils.utc_from_timestamp(
                    subscription_item.current_period_start
                ),
                current_period_end=datetime_utils.utc_from_timestamp(
                    subscription_item.current_period_end
                ),
                cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            )
            self.db_session.add(subscription)

        try:
            self.db_session.commit()
        except IntegrityError:  # race condition
            self.db_session.rollback()
        except Exception as e:
            self.db_session.rollback()
            err_msg = f"Failed to fulfill subscription for payment {payment_id}: {e}"
            logger.exception(err_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err_msg,
            )

    def __handle_subscription_updated_or_deleted(
        self, stripe_subscription: stripe.Subscription
    ) -> None:
        """Handle plan changes, cancellations, expired subscriptions."""
        stripe_subscription_id = stripe_subscription.id
        subscription = self.db_session.exec(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        ).first()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with Stripe ID {stripe_subscription_id} not found in DB",
            )

        subscription_item = stripe_subscription.items.data[0]
        subscription.status = SubscriptionStatus(stripe_subscription.status)
        subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end
        subscription.current_period_start = datetime_utils.utc_from_timestamp(
            subscription_item.current_period_start
        )
        subscription.current_period_end = datetime_utils.utc_from_timestamp(
            subscription_item.current_period_end
        )

        try:
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            err_msg = f"Failed to update subscription with Stripe ID {stripe_subscription_id}: {e}"
            logger.exception(err_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err_msg,
            )

    def __handle_invoice_payment_succeeded(self, invoice: stripe.Invoice) -> None:
        """Handle recurring subscription renewals."""
        if invoice.billing_reason == "subscription_create":
            return  # Initial checkout is handled separately

        stripe_invoice_id = invoice.id
        existing_payment = self.db_session.exec(
            select(Payment).where(Payment.stripe_invoice_id == invoice.id)
        ).first()
        if existing_payment:  # race condition
            return

        meta_dict = invoice.parent.subscription_details.metadata
        meta = SubscriptionMetadata(meta_dict)
        reader_id = meta.reader_id

        try:
            payment = Payment(
                reader_id=reader_id,
                amount_cents=invoice.amount_paid,
                currency=invoice.currency,
                stripe_invoice_id=stripe_invoice_id,
                status=PaymentStatus.SUCCEEDED,
            )
            self.db_session.add(payment)
            self.db_session.commit()
        except IntegrityError:  # race condition
            self.db_session.rollback()
        except Exception as e:
            self.db_session.rollback()
            err_msg = f"Failed to record renewal payment for Stripe invoice {stripe_invoice_id}: {e}"
            logger.exception(err_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err_msg,
            )
