from sqlmodel import Field, Column, UniqueConstraint
from typing import Optional
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class Entitlement(StrictModel, table=True):
    __tablename__ = "entitlement"

    id: Optional[int] = Field(default=None, primary_key=True)

    reader_id: int = Field(foreign_key="readers.id")
    article_id: int = Field(foreign_key="articles.id")

    price_paid: int = Field(description="price at time of purchase")
    purchased_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )

    __table_args__ = (
        UniqueConstraint("reader_id", "article_id", name="uq_reader_article"),
    )
