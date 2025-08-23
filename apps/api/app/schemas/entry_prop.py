from pydantic import BaseModel
from typing import List, Dict, Any


class EntryPropBase(BaseModel):
    key: str
    value_text: str | None = None


class EntryPropCreate(EntryPropBase):
    entry_id: int


class EntryProp(EntryPropBase):
    id: int
    entry_id: int

    class Config:
        from_attributes = True


class EntryPropBatch(BaseModel):
    props: List[EntryPropBase]