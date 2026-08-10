from fastapi import HTTPException, status
from sqlmodel import Session as DBSession, select
from typing import Optional
from sqlalchemy.exc import IntegrityError

from app.db.models.reader import Reader
from app.utils.datetime import datetime_utils


class ReadersService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    def get_by_email(self, email: str) -> Optional[Reader]:
        return self.db_session.exec(select(Reader).where(Reader.email == email)).first()

    def get_by_email_or_create(self, email: str) -> Reader:
        reader = self.get_by_email(email)
        if not reader:
            try:
                reader = Reader(email=email)
                self.db_session.add(reader)
                self.db_session.commit()
                self.db_session.refresh(reader)
            except IntegrityError:  # Handle race condition
                self.db_session.rollback()
                reader = self.db_session.exec(
                    select(Reader).where(Reader.email == email)
                ).one()
        return reader

    def verify_reader(self, email: str):
        reader = self.get_by_email(email)
        if not reader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found"
            )

        if not reader.verified_at:
            try:
                reader.verified_at = datetime_utils.now_utc()
                self.db_session.commit()
            except Exception:
                self.db_session.rollback()
                raise
