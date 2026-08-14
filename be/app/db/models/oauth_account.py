from enum import Enum
from typing import Optional
from datetime import datetime
from sqlmodel import Field, Column, UniqueConstraint
from sqlalchemy import Enum as SQLEnum

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class OAuthProvider(str, Enum):
    GOOGLE = "google"


class OAuthAccount(StrictModel, table=True):
    __tablename__ = "oauth_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    reader_id: int = Field(foreign_key="readers.id")

    provider: OAuthProvider = Field(
        sa_column=Column(SQLEnum(OAuthProvider, native_enum=False), nullable=False)
    )
    provider_account_id: str
    email: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )

    __table_args__ = (
        UniqueConstraint("reader_id", "provider"),
        UniqueConstraint("provider", "provider_account_id"),
    )