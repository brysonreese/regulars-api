from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.places import PlaceRead


class ReviewCreate(BaseModel):
    user_id: UUID
    apple_place_id: str = Field(min_length=1)
    rating: int = Field(strict=True, ge=1, le=10)
    body: str | None = None
    visibility: int = Field(strict=True, ge=0, le=1)


class ReviewUpdate(BaseModel):
    rating: int = Field(strict=True, ge=1, le=10)
    body: str | None
    visibility: int = Field(strict=True, ge=0, le=1)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    place_id: UUID
    place: PlaceRead
    rating: int
    body: str | None
    visibility: int
    created_at: datetime
    updated_at: datetime
