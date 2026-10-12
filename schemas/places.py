from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlaceCreate(BaseModel):
    apple_place_id: str = Field(min_length=1)


class PlaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    apple_place_id: str
