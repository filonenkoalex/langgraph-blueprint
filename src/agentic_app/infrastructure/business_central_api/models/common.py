"""Common shared models for OData responses."""

from pydantic import BaseModel


class ODataResponse[T](BaseModel):
    """Generic OData wrapper that holds a list of arbitrary entity models."""

    value: list[T]
