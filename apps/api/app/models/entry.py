from sqlalchemy import ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hobby import Hobby
    from .hobby_type import HobbyType
    from .entry_media import EntryMedia
    from .entry_prop import EntryProp


class Entry(Base, TimestampMixin):
    __tablename__ = "entry"
    __table_args__ = (
        Index("idx_entry_hobby", "hobby_id"),
        Index("idx_entry_type", "type_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hobby_id: Mapped[int] = mapped_column(
        ForeignKey("hobby.id", ondelete="CASCADE"), nullable=False
    )
    type_key: Mapped[str] = mapped_column(
        ForeignKey("hobbytype.key"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    hobby: Mapped["Hobby"] = relationship("Hobby", back_populates="entries")
    hobby_type: Mapped["HobbyType"] = relationship("HobbyType", back_populates="entries")
    media: Mapped[list["EntryMedia"]] = relationship(
        "EntryMedia", back_populates="entry", cascade="all, delete-orphan"
    )
    props: Mapped[list["EntryProp"]] = relationship(
        "EntryProp", back_populates="entry", cascade="all, delete-orphan"
    )
    tags_rel: Mapped[list["EntryTag"]] = relationship(
        "EntryTag", back_populates="entry", cascade="all, delete-orphan"
    )
