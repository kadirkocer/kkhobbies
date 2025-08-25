from typing import Literal

from pydantic import BaseModel


class EntryMediaBase(BaseModel):
    kind: Literal["image", "video", "audio", "doc"] | None = None
    file_path: str
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    meta_json: str | None = None


class EntryMediaCreate(EntryMediaBase):
    entry_id: int


class EntryMedia(EntryMediaBase):
    id: int
    entry_id: int

    class Config:
        from_attributes = True
