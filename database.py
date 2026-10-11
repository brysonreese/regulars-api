import os
from functools import lru_cache

from sqlalchemy import create_engine, make_url
from sqlalchemy.engine import Engine


@lru_cache
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")

    return create_engine(url, pool_pre_ping=True)
