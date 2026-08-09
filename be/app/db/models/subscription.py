from sqlmodel import Field, Column
from typing import Optional
from enum import Enum
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class SubscriptionStatus(str, Enum):
    """Match Stripe subscription status."""

    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    TRIALING = "trialing"
    UNPAID = "unpaid"


class Subscription(StrictModel, table=True):
    __tablename__ = "subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    reader_id: int = Field(foreign_key="readers.id")

    stripe_subscription_id: str = Field(unique=True)
    stripe_price_id: str
    status: SubscriptionStatus = Field(description="Stripe subscription status")

    current_period_start: datetime = Field(
        sa_column=Column(UTCDateTime, nullable=False)
    )
    current_period_end: datetime = Field(sa_column=Column(UTCDateTime, nullable=False))
    cancel_at_period_end: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
