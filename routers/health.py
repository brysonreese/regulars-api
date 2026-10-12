from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import get_engine

router = APIRouter(tags=["health"])


@router.get("/")
def home():
    return {"message": "Regulars API is running!"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/db-check")
def database_check():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

    return {"database": "connected"}
