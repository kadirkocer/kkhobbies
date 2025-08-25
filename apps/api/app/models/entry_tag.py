from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .entry import Entry


class EntryTag(Base):
    __tablename__ = "entrytag"
    __table_args__ = (
        Index("ix_entrytag_entry", "entry_id"),
        Index("ix_entrytag_tag", "tag"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("entry.id", ondelete="CASCADE"), nullable=False)
    tag: Mapped[str] = mapped_column(String(100), nullable=False)

    entry: Mapped["Entry"] = relationship("Entry", back_populates="tags_rel")

