"""OData Response."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ODataResponse(BaseModel, Generic[T]):
    """Generic OData wrapper that holds a list of arbitrary entity models."""

    value: list[T]
