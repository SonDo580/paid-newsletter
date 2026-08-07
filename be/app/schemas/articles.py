from pydantic import BaseModel, Field, AfterValidator, ConfigDict
from typing import Optional, Annotated
import re
from datetime import datetime
from enum import Enum

from app.schemas.shared import TStrippedStr, SortOrder


def validate_slug_format(v: str) -> str:
    if not re.match(r"^[a-z0-9-]+$", v):
        raise ValueError("Slug must contain only lowercase letters, numbers, hyphens")
    if v.startswith("-") or v.endswith("-"):
        raise ValueError("Slug cannot start or end with hyphen")
    return v


TSlug = Annotated[
    TStrippedStr,
    Field(min_length=3, max_length=150),
    AfterValidator(validate_slug_format),
]
TTitle = Annotated[TStrippedStr, Field(min_length=10, max_length=150)]
TContent = Annotated[TStrippedStr, Field(min_length=100)]


class ArticleCreateReqBody(BaseModel):
    title: TTitle
    content: TContent
    slug: TSlug = Field(
        description="FE generates from title and allow editing. "
        "BE provides endpoint to check slug uniqueness.",
    )
    is_free: bool = False
    is_published: bool = False


class ArticleCreateResBody(BaseModel):
    id: int


class CheckSlugResBody(BaseModel):
    available: bool


class ArticleUpdateReqBody(BaseModel):
    title: Optional[TTitle] = None
    content: Optional[TContent] = None
    is_free: Optional[bool] = None
    is_published: Optional[bool] = None
    # Don't allow updating 'slug' to prevent breaking existing link.


class AccessStatus(str, Enum):
    FULL = "full"
    TEASER = "teaser"


class PublicArticle(BaseModel):
    """Show to readers."""

    id: int
    title: str
    slug: str
    content: str
    published_at: datetime
    access_status: AccessStatus
    past_due_subscription: bool = False


class ArticleSortBy(str, Enum):
    ID = "id"
    TITLE = "title"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PUBLISHED_AT = "published_at"


class ArticlesListForAdminParams(BaseModel):
    # === Paging ===
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    # === Keyword search ===
    keyword: Optional[TStrippedStr] = Field(
        default=None, max_length=100, description="Search in title, slug, content"
    )

    # === Filter ===
    is_free: Optional[bool] = None
    is_published: Optional[bool] = None

    # created_after: Optional[datetime] = None
    # created_before: Optional[datetime] = None
    # updated_after: Optional[datetime] = None
    # updated_before: Optional[datetime] = None
    # published_after: Optional[datetime] = None
    # published_before: Optional[datetime] = None

    # === Sort ===
    sort_by: ArticleSortBy = ArticleSortBy.ID
    sort_order: SortOrder = SortOrder.DESC


class ArticlesListItemForAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    is_free: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]


class ArticlesListForAdminResBody(BaseModel):
    items: list[ArticlesListItemForAdmin]
    total: int


class ArticlesListForReaderParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=50)
    cursor: Optional[str] = None


class ArticlesListItemForReader(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str


class ArticlesListForReaderResBody(BaseModel):
    items: list[ArticlesListItemForReader]
    next_cursor: Optional[str] = None
