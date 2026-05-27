"""Common Pydantic schemas: pagination, generic responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""

    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        """Calculate the SQL offset for this page."""
        return (self.page - 1) * self.size


class Page(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> "Page[T]":
        """Factory method to construct a Page from query results."""
        pages = max(1, -(-total // size))  # ceiling division
        return cls(items=items, total=total, page=page, size=size, pages=pages)


class ErrorResponse(BaseModel):
    """Standard error response shape."""

    detail: str
    code: str
    timestamp: str
