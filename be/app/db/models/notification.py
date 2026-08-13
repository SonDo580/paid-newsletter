from enum import Enum
from typing import Optional
from sqlmodel import Field, UniqueConstraint, Column
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class Notification(StrictModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id")
    reader_id: int = Field(foreign_key="readers.id")

    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime),
    )
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(UTCDateTime, nullable=True),
    )

    __table_args__ = (UniqueConstraint("article_id", "reader_id"),)
