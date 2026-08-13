from fastapi import APIRouter, status, Depends

from app.db.models.article import Article
from app.schemas.articles import (
    TSlug,
    ArticleCreateReqBody,
    ArticleCreateResBody,
    CheckSlugResBody,
    ArticleUpdateReqBody,
    PublicArticle,
    ArticlesListForAdminParams,
    ArticlesListForAdminResBody,
    ArticlesListForReaderParams,
    ArticlesListForReaderResBody,
)
from app.dependencies.auth import AdminRequiredDep, OptionalUserDep
from app.dependencies.services import ArticlesServiceDep

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "/", response_model=ArticleCreateResBody, status_code=status.HTTP_201_CREATED
)
async def create_article(
    data: ArticleCreateReqBody,
    articles_service: ArticlesServiceDep,
    _: AdminRequiredDep,
):
    return await articles_service.create_article(data)


@router.get("/check-slug", response_model=CheckSlugResBody)
def check_slug(slug: TSlug, articles_service: ArticlesServiceDep, _: AdminRequiredDep):
    """Checks if a slug is available."""
    available = articles_service.is_slug_unique(slug)
    return CheckSlugResBody(available=available)


@router.patch("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_article(
    article_id: int,
    data: ArticleUpdateReqBody,
    articles_service: ArticlesServiceDep,
    _: AdminRequiredDep,
):
    """Can do the followings:
    - Update content.
    - Toggle free/paid status.
    - Publish/unpublish. Trigger email sending for first-time publish.
    """
    await articles_service.update_article(article_id, data)


@router.get("/id/{article_id}", response_model=Article)
def get_article_by_id(
    article_id: int, articles_service: ArticlesServiceDep, _: AdminRequiredDep
):
    """Find article by ID - for admin."""
    return articles_service.get_by_id(article_id)


@router.get(
    "/slug/{slug}",
    response_model=PublicArticle,
)
def get_article_by_slug(
    slug: TSlug,
    articles_service: ArticlesServiceDep,
    user: OptionalUserDep,
):
    """Find article by slug. Paywall is applied to readers and anonymous guests."""
    return articles_service.get_by_slug(slug, user)


@router.get("/list/reader", response_model=ArticlesListForReaderResBody)
def list_articles_for_reader(
    articles_service: ArticlesServiceDep,
    params: ArticlesListForReaderParams = Depends(),
):
    """List articles for readers and anonymous guests."""
    return articles_service.list_articles_for_reader(params)


@router.get("/list/admin", response_model=ArticlesListForAdminResBody)
def list_articles_for_admin(
    articles_service: ArticlesServiceDep,
    _: AdminRequiredDep,
    params: ArticlesListForAdminParams = Depends(),
):
    return articles_service.list_articles_for_admin(params)
