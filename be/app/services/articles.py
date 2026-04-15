from sqlmodel import Session as DBSession, select
from fastapi import HTTPException, status

from app.db.models.article import Article
from app.db.models.deleted_article import DeletedArticle
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
        """
        Find article by slug - for public readers.
        Handle paywall logic.
        Inform readers if article has been deleted.
        """
        article = db_session.exec(
            select(Article).where(Article.slug == slug, Article.is_published == True)
        ).first()
        if article:
            # TODO: Handle paywall logic
            return article

        # If not found, check if article has been deleted
        # (there may be multiple deleted articles with the same slug)
        deleted_info = db_session.exec(
            select(DeletedArticle).where(DeletedArticle.slug == slug)
        ).first()
        if deleted_info:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Article has been deleted",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

    @staticmethod
    def delete_article(db_session: DBSession, article_id: int):
        """Remove article from active table and move to graveyard."""
        article = ArticlesService.get_by_id(db_session, article_id)
        try:
            # Add graveyard entry
            deleted_entry = DeletedArticle(
                article_id=article.id, slug=article.slug, title=article.title
            )
            db_session.add(deleted_entry)

            # Delete the active record
            db_session.delete(article)

            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

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

        for k, v in update_data.items():
            setattr(article, k, v)  # can do this only if field names match

        now = datetime_utils.now_utc()
        article.updated_at = now
        if is_first_publish:
            article.published_at = now
            # TODO: email notification to subscribers

        try:
            db_session.add(article)  # update if id is set
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
