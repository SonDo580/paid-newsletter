import stripe
import resend

from app.config.settings import settings


def init_sdks():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    resend.api_key = settings.RESEND_API_KEY
