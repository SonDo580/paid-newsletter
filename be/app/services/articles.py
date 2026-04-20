from sqlmodel import Session as DBSession, select
from fastapi import HTTPException, status

from app.db.models.article import Article
from app.schemas.articles import (
    ArticleCreateReqBody,
    ArticleCreateResBody,
    ArticleUpdateReqBody,
)
from app.utils.datetime import datetime_utils


class ArticlesService:
    @staticmethod
    def save_draft(
        db_session: DBSession, data: ArticleCreateReqBody
    ) -> ArticleCreateResBody:
        if not ArticlesService.is_slug_unique(db_session, data.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slug is already taken",
            )

        try:
            article = Article(**data.model_dump())
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
    def get_by_slug(db_session: DBSession, slug: str) -> Article:
        """Find article by slug. Apply paywall to readers."""
        # TODO: handle admin
        article = db_session.exec(
            select(Article).where(Article.slug == slug, Article.is_published == True)
        ).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        # TODO: reader should still see unpublished article if purchased before
        # TODO: Handle paywall logic for readers (subscribed or purchased)
        return article

    @staticmethod
    def update_article(
        db_session: DBSession, article_id: int, data: ArticleUpdateReqBody
    ):
        article = ArticlesService.get_by_id(db_session, article_id)
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return

        is_first_publish = (
            data.is_published
            and not article.is_published
            and article.published_at is None
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
