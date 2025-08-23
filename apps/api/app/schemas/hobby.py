from pydantic import BaseModel
from typing import List, Optional


class HobbyBase(BaseModel):
    name: str
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None


class HobbyCreate(HobbyBase):
    pass


class HobbyUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None


class Hobby(HobbyBase):
    id: int
    children: List["Hobby"] = []

    class Config:
        from_attributes = True