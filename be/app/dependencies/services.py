from typing import Annotated
from fastapi import Depends

from app.common.arq_redis import ArqRedisDep
from app.db.connect import DBSessionDep
from app.db.models.oauth_account import OAuthProvider
from app.services.articles import ArticlesService
from app.services.auth import AuthService
from app.services.billing import BillingService
from app.services.checkout import CheckoutService
from app.services.mail import MailService
from app.services.oauth_clients.google import GoogleOAuthProviderClient
from app.services.oauth import OAuthService
from app.services.readers import ReadersService
from app.services.stripe_webhook import StripeWebhookService
from app.services.subscriptions import SubscriptionsService


def get_articles_service(
    db_session: DBSessionDep, arq_redis: ArqRedisDep
) -> ArticlesService:
    return ArticlesService(db_session, arq_redis)


def get_auth_service(db_session: DBSessionDep) -> AuthService:
    return AuthService(db_session)


def get_billing_service(db_session: DBSessionDep) -> BillingService:
    return BillingService(db_session)


def get_checkout_service(db_session: DBSessionDep) -> CheckoutService:
    return CheckoutService(db_session)


def get_mail_service() -> MailService:
    return MailService()


def get_oauth_service(db_session: DBSessionDep) -> OAuthService:
    google_provider = GoogleOAuthProviderClient()
    provider_clients = {OAuthProvider.GOOGLE: google_provider}
    return OAuthService(db_session, provider_clients)


def get_readers_service(db_session: DBSessionDep) -> ReadersService:
    return ReadersService(db_session)


def get_stripe_webhook_service(db_session: DBSessionDep) -> StripeWebhookService:
    return StripeWebhookService(db_session)


def get_subscriptions_service(db_session: DBSessionDep) -> SubscriptionsService:
    return SubscriptionsService(db_session)


ArticlesServiceDep = Annotated[ArticlesService, Depends(get_articles_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]
CheckoutServiceDep = Annotated[CheckoutService, Depends(get_checkout_service)]
MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
OAuthServiceDep = Annotated[OAuthService, Depends(get_oauth_service)]
ReadersServiceDep = Annotated[ReadersService, Depends(get_readers_service)]
StripeWebhookServiceDep = Annotated[
    StripeWebhookService, Depends(get_stripe_webhook_service)
]
SubscriptionsServiceDep = Annotated[
    SubscriptionsService, Depends(get_subscriptions_service)
]
