from sqlmodel import Field, Column
from typing import Optional
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class Reader(StrictModel, table=True):
    __tablename__ = "readers"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    is_subscriber: bool = False

    created_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime, nullable=False),
    )
    verified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(UTCDateTime, nullable=True),
    )
