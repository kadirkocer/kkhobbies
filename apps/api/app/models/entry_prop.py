from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .entry import Entry


class EntryProp(Base):
    __tablename__ = "entryprop"
    __table_args__ = (
        UniqueConstraint("entry_id", "key"),
        Index("idx_entryprop_entry", "entry_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(
        ForeignKey("entry.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    entry: Mapped["Entry"] = relationship("Entry", back_populates="props")
