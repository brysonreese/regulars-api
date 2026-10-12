import os
from collections.abc import Generator
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, make_url
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


@lru_cache
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")

    return create_engine(url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with get_session_factory()() as session:
        yield session
