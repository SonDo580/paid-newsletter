from sqlmodel import Session as DBSession, select, or_, func
from fastapi import HTTPException, status
from typing import Union, Optional
import base64

from app.db.models.article import Article
from app.db.models.entitlement import Entitlement
from app.schemas.articles import (
    ArticleCreateReqBody,
    ArticleCreateResBody,
    ArticleUpdateReqBody,
    PublicArticle,
    AccessStatus,
    ArticlesListForAdminParams,
    ArticlesListItemForAdmin,
    ArticlesListForAdminResBody,
    ArticlesListForReaderParams,
    ArticlesListItemForReader,
    ArticlesListForReaderResBody,
)
from app.schemas.auth import CurrentUser
from app.schemas.shared import SortOrder
from app.utils.datetime import datetime_utils


def encode_cursor(last_id: int) -> str:
    return base64.b64encode(str(last_id).encode()).decode()


def decode_cursor(cursor: str) -> int:
    try:
        return int(base64.b64decode(cursor.encode()).decode())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor"
        )


class ArticlesService:
    @staticmethod
    def create_article(
        db_session: DBSession, data: ArticleCreateReqBody
    ) -> ArticleCreateResBody:
        if not ArticlesService.is_slug_unique(db_session, data.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slug is already taken",
            )

        try:
            article = Article.model_validate(data)
            db_session.add(article)
            db_session.commit()
            db_session.refresh(article)
            return ArticleCreateResBody(id=article.id)
        except Exception:
            db_session.rollback()
            raise
            # Race condition: someone added the same slug between our check and commit
            # -> Don't handle since there's only 1 admin

    @staticmethod
    def is_slug_unique(db_session: DBSession, slug: str) -> bool:
        statement = select(Article.id).where(Article.slug == slug)
        exists = db_session.exec(statement).first()
        return exists is None

    @staticmethod
    def get_by_id(db_session: DBSession, article_id: int) -> Article:
        """Find article by ID - for admin."""
        statement = select(Article).where(Article.id == article_id)
        article = db_session.exec(statement).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )
        return article

    @staticmethod
    def get_by_slug(
        db_session: DBSession, slug: str, user: Optional[CurrentUser]
    ) -> Union[Article, PublicArticle]:
        """Find article by slug.
        Paywall is applied to readers and anonymous guests."""
        article = db_session.exec(select(Article).where(Article.slug == slug)).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        # Bypass checks for admin
        if user and user.is_admin:
            return article

        # Check for specific one-off purchase
        reader = user.reader if user else None
        purchase = None
        if reader:
            purchase = db_session.exec(
                select(Entitlement).where(
                    Entitlement.reader_id == reader.id,
                    Entitlement.article_id == article.id,
                )
            ).first()

        # Handle unpublished article
        if not article.is_published:
            # Article has never been published
            if article.published_at is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Article not found",
                )

            # Article was published before but is currently unpublished
            # -> Only allow access if reader bought article
            if not purchase:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Article has been retired from public view",
                )

        is_subscriber = reader.is_subscriber if reader else False
        if article.is_free or is_subscriber or purchase:
            # Allow full access
            return PublicArticle(
                **article.model_dump(), access_status=AccessStatus.FULL
            )

        # Return teaser
        teaser = article.content[: min(len(article.content) // 5, 300)] + "..."
        return PublicArticle(
            **article.model_dump(exclude={"content"}),
            content=teaser,
            access_status=AccessStatus.TEASER,
        )

    @staticmethod
    def update_article(
        db_session: DBSession, article_id: int, data: ArticleUpdateReqBody
    ):
        article = ArticlesService.get_by_id(db_session, article_id)
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return

        is_first_publish = (
            data.is_published  # request wants to publish
            and not article.is_published  # article is currently not published
            and article.published_at is None  # article has never been published
        )

        try:
            for k, v in update_data.items():
                # can do this only if fields match
                setattr(article, k, v)

            now = datetime_utils.now_utc()
            article.updated_at = now
            if is_first_publish:
                article.published_at = now
                # TODO: email notification to subscribers

            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    @staticmethod
    def list_articles_for_admin(
        db_session: DBSession, params: ArticlesListForAdminParams
    ) -> ArticlesListForAdminResBody:
        # Build filter conditions
        conditions = []
        if params.keyword:
            term = f"%{params.keyword}%"
            conditions.append(
                or_(
                    Article.title.ilike(term),
                    Article.slug.ilike(term),
                    Article.content.ilike(term),
                )
            )
        if params.is_free is not None:
            conditions.append(Article.is_free == params.is_free)
        if params.is_published is not None:
            conditions.append(Article.is_published == params.is_published)

        # Build count stmt
        count_stmt = select(func.count(Article.id)).where(*conditions)

        # Build data stmt with sorting and paging
        sort_column = getattr(Article, params.sort_by.value)
        sort_clause = (
            sort_column.desc()
            if params.sort_order == SortOrder.DESC
            else sort_column.asc()
        )
        offset = (params.page - 1) * params.page_size
        data_stmt = (
            select(Article)
            .where(*conditions)
            .order_by(sort_clause)
            .offset(offset)
            .limit(params.page_size)
        )

        total = db_session.exec(count_stmt).one()
        articles = db_session.exec(data_stmt).all()
        items = [ArticlesListItemForAdmin.model_validate(a) for a in articles]
        return ArticlesListForAdminResBody(items=items, total=total)

    @staticmethod
    def list_articles_for_reader(
        db_session: DBSession, params: ArticlesListForReaderParams
    ) -> ArticlesListForReaderResBody:
        conditions = [Article.is_published == True]
        if params.cursor is not None:
            last_id = decode_cursor(params.cursor)
            conditions.append(Article.id < last_id)  # since order is id DESC

        stmt = (
            select(Article)
            .where(*conditions)
            .order_by(Article.id.desc())
            .limit(params.limit + 1)  # +1 to check if there's more
        )

        articles = db_session.exec(stmt).all()
        has_more = len(articles) > params.limit
        articles = articles[: params.limit]

        next_cursor = None
        if has_more:
            next_cursor = encode_cursor(articles[-1].id)

        items = [ArticlesListItemForReader.model_validate(a) for a in articles]
        return ArticlesListForReaderResBody(items=items, next_cursor=next_cursor)
