from sqlalchemy import event
from sqlmodel import create_engine, Session
import sqlite3
from typing import Annotated
from fastapi import Depends

from app.config.settings import settings


connect_args = {
    "check_same_thread": False  # a DB connection can be shared across threads
}
engine = create_engine(settings.DB_URL, connect_args=connect_args)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection: sqlite3.Connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # improve concurrency
    cursor.execute("PRAGMA synchronous=NORMAL")  # only sync to disk at critical moments
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session():
    with Session(engine) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_session)]
