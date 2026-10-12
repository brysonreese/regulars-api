from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.places import PlaceCreate, PlaceRead
from services.places import get_or_create_place

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", response_model=PlaceRead)
def create_or_get_place(
    place_data: PlaceCreate,
    db: Annotated[Session, Depends(get_db)],
):
    place = get_or_create_place(db, place_data.apple_place_id)
    db.commit()
    return place
