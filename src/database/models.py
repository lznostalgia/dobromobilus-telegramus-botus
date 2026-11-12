from typing import List
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base



class Fosters(Base):
    __tablename__ = "shelter"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    animal_type: Mapped[str] = mapped_column(
        String(30)
    )

    city: Mapped[str] = mapped_column(
        String(30)
    )

    address: Mapped[str] = mapped_column(
        String(30)
    )

    pets: Mapped[list["Pets"]] = relationship(
        back_populates="shelter"
    )

class Pets(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    animal_type: Mapped[str] = mapped_column(
        String(30)
    )

    city: Mapped[str] = mapped_column(
        String(30)
    )

    address: Mapped[str] = mapped_column(
        String(30)
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

class Applications(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer(10)
    )

    username: Mapped[str | None] = mapped_column(
        String(100)
    )

    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="RESTRICT")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    pet: Mapped["Pets"] = relationship(
        back_populates="applications"
    )