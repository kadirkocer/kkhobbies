from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .entry_media import EntryMedia
from .entry_prop import EntryProp


class EntryBase(BaseModel):
    hobby_id: int
    type_key: str
    title: str | None = None
    description: str | None = None
    tags: str | None = None


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: str | None = None


class EntryListItem(BaseModel):
    id: int
    hobby_id: int
    type_key: str
    title: str | None
    description: str | None
    tags: str | None
    created_at: datetime
    updated_at: datetime | None
    media_count: int = 0
    thumbnail_url: str | None = None
    props: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class Entry(EntryBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
    media: list[EntryMedia] = Field(default_factory=list)
    props: list[EntryProp] = Field(default_factory=list)

    class Config:
        from_attributes = True
