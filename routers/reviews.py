from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from database import get_db
from models import Place, Review, User
from schemas.reviews import ReviewCreate, ReviewRead, ReviewUpdate
from services.places import get_or_create_place

router = APIRouter(prefix="/reviews", tags=["reviews"])

PUBLIC = 1


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, db: Annotated[Session, Depends(get_db)]):
    if db.get(User, review_data.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    place = get_or_create_place(db, review_data.apple_place_id)
    review = Review(
        user_id=review_data.user_id,
        place=place,
        rating=review_data.rating,
        body=review_data.body,
        visibility=review_data.visibility,
    )
    db.add(review)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create review; related data may have changed",
        ) from exc

    db.refresh(review)
    return review


@router.get("", response_model=list[ReviewRead])
def get_reviews(
    db: Annotated[Session, Depends(get_db)],
    user_id: UUID | None = None,
    place_id: UUID | None = None,
    apple_place_id: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
):
    statement = (
        select(Review)
        .where(Review.visibility == PUBLIC)
        .options(selectinload(Review.place))
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    if user_id is not None:
        statement = statement.where(Review.user_id == user_id)
    if place_id is not None:
        statement = statement.where(Review.place_id == place_id)
    if apple_place_id is not None:
        statement = statement.join(Review.place).where(
            Place.apple_place_id == apple_place_id
        )
    if limit is not None:
        statement = statement.limit(limit)
    return db.scalars(statement).all()


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: UUID, db: Annotated[Session, Depends(get_db)]):
    statement = (
        select(Review)
        .where(Review.id == review_id, Review.visibility == PUBLIC)
        .options(selectinload(Review.place))
    )
    review = db.scalar(statement)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.put("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    review.rating = review_data.rating
    review.body = review_data.body
    review.visibility = review_data.visibility
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: UUID, db: Annotated[Session, Depends(get_db)]):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    db.delete(review)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
