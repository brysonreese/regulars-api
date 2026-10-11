from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db, get_engine
from models import User
from schemas import UserCreate, UserRead, UserUpdate

app = FastAPI(
    title="Regulars API",
    version="0.1.0",
)


@app.get("/")
def home():
    return {"message": "Regulars API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
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


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    user = User(**user_data.model_dump())
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create user; the username may already be in use",
        ) from exc

    db.refresh(user)
    return user


@app.get("/users", response_model=list[UserRead])
def get_users(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.username = user_data.username
    user.display_name = user_data.display_name

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update user; the username may already be in use",
        ) from exc

    db.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
