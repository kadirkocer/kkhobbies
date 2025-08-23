from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class ErrorResponse(BaseModel):
    status: int
    code: str
    message: str
    details: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool