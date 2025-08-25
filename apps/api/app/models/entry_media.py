from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .entry import Entry


class EntryMedia(Base):
    __tablename__ = "entrymedia"
    __table_args__ = (
        Index("idx_media_entry", "entry_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(
        ForeignKey("entry.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str | None] = mapped_column(
        String(20),
        CheckConstraint("kind IN ('image', 'video', 'audio', 'doc')"),
        nullable=True,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    entry: Mapped["Entry"] = relationship("Entry", back_populates="media")
