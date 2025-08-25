
from pydantic import BaseModel, Field


class HobbyBase(BaseModel):
    name: str
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None
    slug: str | None = None
    description: str | None = None
    sort_order: int | None = 0
    config_json: str | None = None


class HobbyCreate(HobbyBase):
    pass


class HobbyUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    parent_id: int | None = None
    slug: str | None = None
    description: str | None = None
    sort_order: int | None = None
    config_json: str | None = None


class Hobby(HobbyBase):
    id: int
    children: list["Hobby"] = Field(default_factory=list)

    class Config:
        from_attributes = True
