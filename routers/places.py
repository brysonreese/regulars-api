from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database import get_db
from models import Place
from schemas.places import PlaceCreate, PlaceRead

router = APIRouter(prefix="/places", tags=["places"])


def get_or_create_place(db: Session, apple_place_id: str) -> Place:
    statement = (
        insert(Place)
        .values(apple_place_id=apple_place_id)
        .on_conflict_do_nothing(index_elements=[Place.apple_place_id])
        .returning(Place)
    )

    place = db.scalar(statement)
    if place is not None:
        return place

    place = db.scalar(select(Place).where(Place.apple_place_id == apple_place_id))
    if place is None:
        raise RuntimeError("Place was not found after insert conflict")
    return place


@router.post("", response_model=PlaceRead)
def create_or_get_place(
    place_data: PlaceCreate,
    db: Annotated[Session, Depends(get_db)],
):
    place = get_or_create_place(db, place_data.apple_place_id)
    db.commit()
    return place
