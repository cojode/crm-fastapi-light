from pydantic import BaseModel, ConfigDict, Field

from typing import TypeVar, Generic

from src.logger import ServiceOutputLoggerMixin

T = TypeVar("T")


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GenericResponseMessageField(BaseModel):
    msg: str = Field(default="success")


class GenericResponse(
    GenericResponseMessageField, ServiceOutputLoggerMixin, Generic[T]
):
    data: T | None


class GenericListResponse(
    GenericResponseMessageField, ServiceOutputLoggerMixin, Generic[T]
):
    values: list[T]
    count: int = Field(default_factory=lambda r: len(r["values"]))
