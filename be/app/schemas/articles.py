from pydantic import BaseModel, Field, AfterValidator
from typing import Optional, Annotated
import re
from datetime import datetime

from app.schemas.shared import TStrippedStr


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


class ArticlePublicResBody(BaseModel):
    title: str
    slug: str
    content: str
    published_at: datetime
    is_free: bool
