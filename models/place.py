import uuid

from sqlalchemy import Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    apple_place_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
