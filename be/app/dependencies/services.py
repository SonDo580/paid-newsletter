from typing import Annotated
from fastapi import Depends

from app.db.connect import DBSessionDep
from app.services.articles import ArticlesService
from app.services.auth import AuthService
from app.services.billing import BillingService
from app.services.checkout import CheckoutService
from app.services.mail import MailService
from app.services.readers import ReadersService
from app.services.stripe_webhook import StripeWebhookService


def get_articles_service(db_session: DBSessionDep) -> ArticlesService:
    return ArticlesService(db_session)


def get_auth_service(db_session: DBSessionDep) -> AuthService:
    return AuthService(db_session)


def get_billing_service(db_session: DBSessionDep) -> BillingService:
    return BillingService(db_session)


def get_checkout_service(db_session: DBSessionDep) -> CheckoutService:
    return CheckoutService(db_session)


def get_mail_service() -> MailService:
    return MailService()


def get_readers_service(db_session: DBSessionDep) -> ReadersService:
    return ReadersService(db_session)


def get_stripe_webhook_service(db_session: DBSessionDep) -> StripeWebhookService:
    return StripeWebhookService(db_session)


ArticlesServiceDep = Annotated[ArticlesService, Depends(get_articles_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]
CheckoutServiceDep = Annotated[CheckoutService, Depends(get_checkout_service)]
MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
ReadersServiceDep = Annotated[ReadersService, Depends(get_readers_service)]
StripeWebhookServiceDep = Annotated[
    StripeWebhookService, Depends(get_stripe_webhook_service)
]
