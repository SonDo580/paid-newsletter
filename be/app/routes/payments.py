from fastapi import APIRouter, Depends, Request

from app.dependencies.auth import get_current_reader
from app.db.connect import DBSessionDep
from app.db.models.reader import Reader
from app.schemas.payments import (
    PurchaseCheckoutReqBody,
    SubscriptionCheckoutReqBody,
    CheckoutResBody,
)
from app.services.checkout import CheckoutService
from app.services.stripe_webhook import StripeWebhookService

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


@router.delete("/subscriptions")
def unsubscribe(
    db_session: DBSessionDep,
    reader: Reader = Depends(get_current_reader),
):
    pass


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db_session: DBSessionDep):
    stripe_webhook_service = StripeWebhookService(db_session)
    event = await stripe_webhook_service.verify_request(request)
    stripe_webhook_service.handle_event(event)
    return {"status": "success"}
