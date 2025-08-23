from pydantic import BaseModel
from typing import Optional
from .entry import EntryListItem


class SearchRequest(BaseModel):
    q: str
    hobby_id: int | None = None
    type_key: str | None = None
    tag: str | None = None


class SearchResult(BaseModel):
    entry: EntryListItem
    rank: float