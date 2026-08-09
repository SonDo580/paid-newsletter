from pydantic import BaseModel
from typing import Literal


class PurchaseCheckoutReqBody(BaseModel):
    article_id: int
    redirect_path: str


class SubscriptionCheckoutReqBody(BaseModel):
    redirect_path: str


class CheckoutResBody(BaseModel):
    checkout_url: str


class StripeMetadata(BaseModel):
    def to_stripe_metadata(self) -> dict[str, str]:
        """Convert all field values to strings."""
        return {k: str(v) for k, v in self.model_dump().items()}


class CheckoutMetadata(StripeMetadata):
    checkout_type: Literal["purchase", "subscription"]


class PurchaseCheckoutMetadata(CheckoutMetadata):
    payment_id: int
    article_id: int
    reader_id: int


class SubscriptionCheckoutMetadata(CheckoutMetadata):
    payment_id: int
    reader_id: int


class SubscriptionMetadata(StripeMetadata):
    reader_id: int
