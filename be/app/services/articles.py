from sqlmodel import Session as DBSession, select, or_, func
from fastapi import HTTPException, status
from typing import Optional
import base64
from arq.connections import ArqRedis
from loguru import logger

from app.db.models.article import Article
from app.db.models.entitlement import Entitlement
from app.db.models.subscription import SubscriptionStatus
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
from app.services.subscriptions import SubscriptionsService
from app.worker import TaskName


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
    def __init__(self, db_session: DBSession, arq_redis: ArqRedis):
        self.db_session = db_session
        self.arq_redis = arq_redis
        self.subscriptions_service = SubscriptionsService(db_session)

    async def create_article(self, data: ArticleCreateReqBody) -> ArticleCreateResBody:
        if not self.is_slug_unique(data.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slug is already taken",
            )

        try:
            article = Article.model_validate(data)
            if data.is_published:
                article.published_at = datetime_utils.now_utc()
            self.db_session.add(article)
            self.db_session.flush()  # populate article.id
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise

        if article.is_published:
            await self.__notify_subscribers(article.id)

        return ArticleCreateResBody(id=article.id)

    async def update_article(self, article_id: int, data: ArticleUpdateReqBody):
        article = self.get_by_id(article_id)
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
                setattr(article, k, v)  # can do this since fields match
            now = datetime_utils.now_utc()
            article.updated_at = now
            if is_first_publish:
                article.published_at = now
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise

        if is_first_publish:
            await self.__notify_subscribers(article.id)

    async def __notify_subscribers(self, article_id: int):
        await self.arq_redis.enqueue_job(
            TaskName.CREATE_ARTICLE_NOTIFICATIONS, article_id=article_id
        )

    def is_slug_unique(self, slug: str) -> bool:
        statement = select(Article.id).where(Article.slug == slug)
        exists = self.db_session.exec(statement).first()
        return exists is None

    def get_by_id(self, article_id: int) -> Article:
        """Find article by ID - for admin."""
        statement = select(Article).where(Article.id == article_id)
        article = self.db_session.exec(statement).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )
        return article

    def get_by_slug(self, slug: str, user: Optional[CurrentUser]) -> PublicArticle:
        """Find article by slug. Paywall is applied to readers and anonymous guests."""
        article = self.db_session.exec(
            select(Article).where(Article.slug == slug)
        ).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        # Bypass checks for admin
        if user and user.is_admin:
            return PublicArticle(
                **article.model_dump(), access_status=AccessStatus.FULL
            )

        # Check for specific one-off purchase
        reader = user.reader if user else None
        purchased = False
        if reader:
            entitlement = self.db_session.exec(
                select(Entitlement).where(
                    Entitlement.reader_id == reader.id,
                    Entitlement.article_id == article.id,
                )
            ).first()
            purchased = entitlement is not None

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
            if not purchased:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Article has been retired from public view",
                )

        has_active_subscription = False
        if reader:
            subscription = self.subscriptions_service.get_latest_subscription(reader)
            has_active_subscription = (
                subscription is not None
                and subscription.status
                in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
            )

        if article.is_free or has_active_subscription or purchased:
            # Allow full access
            return PublicArticle(
                **article.model_dump(), access_status=AccessStatus.FULL
            )

        # Return teaser
        teaser = article.content[: min(len(article.content) // 5, 300)] + "..."
        subscription_is_past_due = (
            subscription is not None
            and subscription.status == SubscriptionStatus.PAST_DUE
        )
        return PublicArticle(
            **article.model_dump(exclude={"content"}),
            content=teaser,
            access_status=AccessStatus.TEASER,
            past_due_subscription=subscription_is_past_due,
        )

    def list_articles_for_admin(
        self, params: ArticlesListForAdminParams
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

        total = self.db_session.exec(count_stmt).one()
        articles = self.db_session.exec(data_stmt).all()
        items = [ArticlesListItemForAdmin.model_validate(a) for a in articles]
        return ArticlesListForAdminResBody(items=items, total=total)

    def list_articles_for_reader(
        self, params: ArticlesListForReaderParams
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

        articles = self.db_session.exec(stmt).all()
        has_more = len(articles) > params.limit
        articles = articles[: params.limit]

        next_cursor = None
        if has_more:
            next_cursor = encode_cursor(articles[-1].id)

        items = [ArticlesListItemForReader.model_validate(a) for a in articles]
        return ArticlesListForReaderResBody(items=items, next_cursor=next_cursor)
