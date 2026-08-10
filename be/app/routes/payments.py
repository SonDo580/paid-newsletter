from fastapi import APIRouter, Depends, Request

from app.dependencies.auth import get_current_reader
from app.db.connect import DBSessionDep
from app.db.models.reader import Reader
from app.schemas.payments import (
    PurchaseCheckoutReqBody,
    SubscriptionCheckoutReqBody,
    CheckoutResBody,
    CreatePortalSessionReqBody,
    CreatePortalSessionResBody,
)
from app.services.checkout import CheckoutService
from app.services.stripe_webhook import StripeWebhookService
from app.services.billing import BillingService

router = APIRouter(tags=["Payments"])


@router.post("/checkout/purchase", response_model=CheckoutResBody)
def purchase(
    db_session: DBSessionDep,
    payload: PurchaseCheckoutReqBody,
    reader: Reader = Depends(get_current_reader),
):
    checkout_service = CheckoutService(db_session)
    checkout_url = checkout_service.create_purchase_checkout(reader, payload)
    return CheckoutResBody(checkout_url=checkout_url)


@router.post("/checkout/subscription", response_model=CheckoutResBody)
def subscribe(
    db_session: DBSessionDep,
    payload: SubscriptionCheckoutReqBody,
    reader: Reader = Depends(get_current_reader),
):
    checkout_service = CheckoutService(db_session)
    checkout_url = checkout_service.create_subscription_checkout(reader, payload)
    return CheckoutResBody(checkout_url=checkout_url)


@router.post("/billing/portal", response_model=CreatePortalSessionResBody)
def create_portal_session(
    db_session: DBSessionDep,
    payload: CreatePortalSessionReqBody,
    reader: Reader = Depends(get_current_reader),
):
    billing_service = BillingService(db_session)
    portal_url = billing_service.create_portal_session(reader, payload)
    return CreatePortalSessionResBody(portal_url=portal_url)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db_session: DBSessionDep):
    stripe_webhook_service = StripeWebhookService(db_session)
    event = await stripe_webhook_service.verify_request(request)
    stripe_webhook_service.handle_event(event)
    return {"status": "success"}
