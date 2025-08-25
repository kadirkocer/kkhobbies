from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
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
    username: str | None = None  # Optional for single-user setup
    password: str
