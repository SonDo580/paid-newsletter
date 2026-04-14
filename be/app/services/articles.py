from sqlmodel import Session as DBSession, select, desc
from fastapi import HTTPException, status

from app.db.models.article import Article
from app.db.models.deleted_article import DeletedArticle
from app.schemas.articles import ArticleCreateReqBody, ArticleCreateResBody


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
            # Race condition: someone added the same slug between our check and commit
            # -> Don't handle since there's only 1 admin
            raise

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
