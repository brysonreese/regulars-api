from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    display_name: str


class UserUpdate(BaseModel):
    username: str
    display_name: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: str
    created_at: datetime
    updated_at: datetime
