from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models import Place


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
