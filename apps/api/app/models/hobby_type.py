from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entry import Entry


class HobbyType(Base):
    __tablename__ = "hobbytype"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="hobby_type")