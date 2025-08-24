from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entry import Entry


class Hobby(Base):
    __tablename__ = "hobby"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("hobby.id"), nullable=True
    )
    slug: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    parent: Mapped["Hobby | None"] = relationship("Hobby", remote_side=[id], back_populates="children")
    children: Mapped[list["Hobby"]] = relationship("Hobby", back_populates="parent")
    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="hobby")
