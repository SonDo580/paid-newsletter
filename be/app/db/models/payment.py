from sqlmodel import Field, Column
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLEnum

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(StrictModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    reader_id: int = Field(foreign_key="readers.id")

    amount_cents: int
    currency: str
    stripe_payment_intent_id: Optional[str] = Field(default=None, unique=True)
    stripe_invoice_id: Optional[str] = Field(default=None, unique=True)
    status: PaymentStatus = Field(
        sa_column=Column(SQLEnum(PaymentStatus, native_enum=False), nullable=False),
    )

    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
