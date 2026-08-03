from fastapi import APIRouter, status, Depends
from typing import Union, Optional

from app.db.connect import DBSessionDep
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
from app.services.articles import ArticlesService
from app.schemas.auth import CurrentUser
from app.dependencies.auth import admin_required, get_optional_user

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "/", response_model=ArticleCreateResBody, status_code=status.HTTP_201_CREATED
)
def create_article(
    data: ArticleCreateReqBody, db_session: DBSessionDep, _=Depends(admin_required)
):
    return ArticlesService.create_article(db_session, data)


@router.get("/check-slug", response_model=CheckSlugResBody)
def check_slug(slug: TSlug, db_session: DBSessionDep, _=Depends(admin_required)):
    """Checks if a slug is available."""
    available = ArticlesService.is_slug_unique(db_session, slug)
    return CheckSlugResBody(available=available)


@router.patch("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_article(
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


@router.get("/id/{article_id}", response_model=Article)
def get_article_by_id(
    article_id: int, db_session: DBSessionDep, _=Depends(admin_required)
):
    """Find article by ID - for admin."""
    return ArticlesService.get_by_id(db_session, article_id)


@router.get(
    "/slug/{slug}",
    response_model=Union[PublicArticle, Article],
)
def get_article_by_slug(
    slug: TSlug,
    db_session: DBSessionDep,
    user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Find article by slug.
    Paywall is applied to readers and anonymous guests."""
    return ArticlesService.get_by_slug(db_session, slug, user)


@router.get("/list/reader", response_model=ArticlesListForReaderResBody)
def list_articles_for_reader(
    db_session: DBSessionDep,
    params: ArticlesListForReaderParams = Depends(),
):
    """List articles for readers and anonymous guests."""
    return ArticlesService.list_articles_for_reader(db_session, params)


@router.get("/list/admin", response_model=ArticlesListForAdminResBody)
def list_articles_for_admin(
    db_session: DBSessionDep,
    params: ArticlesListForAdminParams = Depends(),
    _=Depends(admin_required),
):
    return ArticlesService.list_articles_for_admin(db_session, params)
