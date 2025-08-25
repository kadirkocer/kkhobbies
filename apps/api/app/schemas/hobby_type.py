from pydantic import BaseModel


class HobbyTypeBase(BaseModel):
    key: str
    title: str
    schema_json: str


class HobbyTypeCreate(HobbyTypeBase):
    pass


class HobbyTypeUpdate(BaseModel):
    title: str | None = None
    schema_json: str | None = None


class HobbyType(HobbyTypeBase):
    id: int

    class Config:
        from_attributes = True
