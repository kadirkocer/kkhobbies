from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any
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
    props: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class Entry(EntryBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
    media: List[EntryMedia] = []
    props: List[EntryProp] = []

    class Config:
        from_attributes = True