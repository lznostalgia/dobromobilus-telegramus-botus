from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base



class Shelter(Base):
    __tablename__ = "shelter"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100), index=True)
    address: Mapped[str] = mapped_column(String(255))

    pets: Mapped[list["Pet"]] = relationship(back_populates="shelter")


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    animal_type: Mapped[str] = mapped_column(String(30), index=True)
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
    )

    shelter_id: Mapped[int] = mapped_column(
        ForeignKey("shelter.id", ondelete="RESTRICT"),
        index=True,
    )
    shelter: Mapped["Shelter"] = relationship(back_populates="pets")

    applications: Mapped[list["Application"]] = relationship(
        back_populates="pet"
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(100))
    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    pet: Mapped["Pet"] = relationship(back_populates="applications")
