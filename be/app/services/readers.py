from fastapi import HTTPException, status
from sqlmodel import Session as DBSession, select
from typing import Optional
from sqlalchemy.exc import IntegrityError

from app.db.models.reader import Reader
from app.utils.datetime import datetime_utils


class ReadersService:
    @staticmethod
    def get_by_email(db_session: DBSession, email: str) -> Optional[Reader]:
        return db_session.exec(select(Reader).where(Reader.email == email)).first()

    @staticmethod
    def get_by_email_or_create(db_session: DBSession, email: str) -> Reader:
        reader = ReadersService.get_by_email(db_session, email)
        if not reader:
            try:
                reader = Reader(email=email)
                db_session.add(reader)
                db_session.commit()
                db_session.refresh(reader)
            except IntegrityError:  # Handle race condition
                db_session.rollback()
                reader = db_session.exec(
                    select(Reader).where(Reader.email == email)
                ).one()
        return reader

    @staticmethod
    def verify_reader(db_session: DBSession, email: str):
        reader = ReadersService.get_by_email(db_session, email)
        if not reader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
            )

        if not reader.verified_at:
            try:
                reader.verified_at = datetime_utils.now_utc()
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise
