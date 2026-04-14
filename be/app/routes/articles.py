from fastapi import APIRouter, status

from app.db.connect import DBSessionDep
from app.db.models.article import Article
from app.schemas.articles import (
    TSlug,
    ArticleCreateReqBody,
    ArticleCreateResBody,
    CheckSlugResBody,
    ArticleUpdateReqBody,
    ArticlePublicResBody,
)
from app.services.articles import ArticlesService

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "/draft", response_model=ArticleCreateResBody, status_code=status.HTTP_201_CREATED
)
async def save_draft(data: ArticleCreateReqBody, db_session: DBSessionDep):
    """Create a new draft."""
    return ArticlesService.save_draft(db_session, data)


@router.get("/check-slug", response_model=CheckSlugResBody)
async def check_slug(slug: TSlug, db_session: DBSessionDep):
    """Checks if a slug is available."""
    available = ArticlesService.is_slug_unique(db_session, slug)
    return CheckSlugResBody(available=available)


@router.patch("/{article_id}")
async def update_article(article_id: int, data: ArticleUpdateReqBody):
    """Can do the followings:
    - Update content.
    - Toggle free/paid status.
    - Publish/unpublish. Trigger email sending for first-time publish.
    """
    return data


@router.delete("/{article_id}")
async def delete_article(article_id: int):
    """Permanently remove article."""
    raise NotImplementedError()


@router.get("/")
async def list_articles():
    """Fetch articles according to filter."""
    raise NotImplementedError()


@router.get("/id/{article_id}", response_model=Article)
async def get_article_by_id(
    article_id: int,
    db_session: DBSessionDep,
):
    """Find article by ID - for admin."""
    return ArticlesService.get_by_id(db_session, article_id)


@router.get("/{slug}", response_model=ArticlePublicResBody)
async def get_article_by_slug(
    slug: TSlug,
    db_session: DBSessionDep,
):
    """Find article by slug - for public readers."""
    return ArticlesService.get_by_slug(db_session, slug)
