from sqlmodel import Field, Column
from typing import Optional
from datetime import datetime

from app.db.models.shared import StrictModel, UTCDateTime
from app.utils.datetime import datetime_utils


class DeletedArticle(StrictModel, table=True):
    """
    Tracks permanently deleted articles to provide info for broken links.
    """

    __tablename__ = "deleted_articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(
        index=True, description="not unique (allow reusing deleted slugs, with alert)"
    )
    title: str = Field("article title (for context)")
    deleted_at: datetime = Field(
        default_factory=datetime_utils.now_utc,
        sa_column=Column(UTCDateTime),
    )
