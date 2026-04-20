from fastapi import APIRouter, status, Depends

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
from app.schemas.auth import CurrentUser
from app.dependencies.auth import admin_required, get_current_user

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "/draft", response_model=ArticleCreateResBody, status_code=status.HTTP_201_CREATED
)
async def save_draft(
    data: ArticleCreateReqBody, db_session: DBSessionDep, _=Depends(admin_required)
):
    """Create a new draft."""
    return ArticlesService.save_draft(db_session, data)


@router.get("/check-slug", response_model=CheckSlugResBody)
async def check_slug(slug: TSlug, db_session: DBSessionDep, _=Depends(admin_required)):
    """Checks if a slug is available."""
    available = ArticlesService.is_slug_unique(db_session, slug)
    return CheckSlugResBody(available=available)


@router.patch("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_article(
    article_id: int,
    data: ArticleUpdateReqBody,
    db_session: DBSessionDep,
    _=Depends(admin_required),
):
    """Can do the followings:
    - Update content.
    - Toggle free/paid status.
    - Publish/unpublish. Trigger email sending for first-time publish.
    """
    ArticlesService.update_article(db_session, article_id, data)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int, db_session: DBSessionDep, _=Depends(admin_required)
):
    """Permanently remove article."""
    ArticlesService.delete_article(db_session, article_id)


@router.get("/")
async def list_articles(
    user: CurrentUser = Depends(get_current_user),
):
    """Fetch articles according to filter."""
    raise NotImplementedError()


@router.get("/id/{article_id}", response_model=Article)
async def get_article_by_id(
    article_id: int, db_session: DBSessionDep, _=Depends(admin_required)
):
    """Find article by ID - for admin."""
    return ArticlesService.get_by_id(db_session, article_id)


@router.get("/{slug}", response_model=ArticlePublicResBody)
async def get_article_by_slug(
    slug: TSlug,
    db_session: DBSessionDep,
    user: CurrentUser = Depends(get_current_user),
):
    """Find article by slug - for public readers."""
    return ArticlesService.get_by_slug(db_session, slug)
