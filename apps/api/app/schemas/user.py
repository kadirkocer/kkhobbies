from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str | None = None
    bio: str | None = None
    avatar_path: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    password: str