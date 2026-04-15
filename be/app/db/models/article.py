from sqlmodel import Field, Column
from typing import Optional
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class Article(StrictModel, table=True):
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(unique=True)
    content: str

    # Paywall
    is_free: bool = False

    # Status
    is_published: bool = Field(default=False, index=True)
    email_sent: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
    published_at: Optional[datetime] = Field(
        default=None, sa_column=Column(UTCDateTime), description="Show to readers"
    )
