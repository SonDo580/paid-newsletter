from fastapi import APIRouter, Request, Body
from typing import Any

from app.schemas.payments import (
    PurchaseCheckoutReqBody,
    SubscriptionCheckoutReqBody,
    CheckoutResBody,
    CreatePortalSessionReqBody,
    CreatePortalSessionResBody,
)
from app.dependencies.auth import CurrentReaderDep
from app.dependencies.services import (
    CheckoutServiceDep,
    BillingServiceDep,
    StripeWebhookServiceDep,
)

router = APIRouter(tags=["Payments"])


@router.post("/checkout/purchase", response_model=CheckoutResBody)
def purchase(
    checkout_service: CheckoutServiceDep,
    payload: PurchaseCheckoutReqBody,
    reader: CurrentReaderDep,
):
    checkout_url = checkout_service.create_purchase_checkout(reader, payload)
    return CheckoutResBody(checkout_url=checkout_url)


@router.post("/checkout/subscription", response_model=CheckoutResBody)
def subscribe(
    checkout_service: CheckoutServiceDep,
    payload: SubscriptionCheckoutReqBody,
    reader: CurrentReaderDep,
):
    checkout_url = checkout_service.create_subscription_checkout(reader, payload)
    return CheckoutResBody(checkout_url=checkout_url)


@router.post("/billing/portal", response_model=CreatePortalSessionResBody)
def create_portal_session(
    billing_service: BillingServiceDep,
    payload: CreatePortalSessionReqBody,
    reader: CurrentReaderDep,
):
    portal_url = billing_service.create_portal_session(reader, payload)
    return CreatePortalSessionResBody(portal_url=portal_url)


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_webhook_service: StripeWebhookServiceDep,
    _: dict[str, Any] = Body(...),
):
    event = await stripe_webhook_service.verify_request(request)
    stripe_webhook_service.handle_event(event)
    return {"status": "success"}
