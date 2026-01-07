import pkgutil
from pathlib import Path

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect


from typing import Any

from dataclasses import fields


class Base(DeclarativeBase):
    """Base for all models."""

    @classmethod
    def from_dataclass(
        cls,
        dc_obj: Any,
        ignore_fields: list[str] | None = None,
        strict_validation: bool = True,
    ) -> "Base":
        """ORM from dataclass"""
        kwargs = {}
        ignore_fields = ignore_fields if ignore_fields else []

        mapper = inspect(cls)

        for field in fields(dc_obj):
            # ? Ignore ignore_fields and skip unnecassary dc fields
            if field.name in ignore_fields or not hasattr(cls, field.name):
                continue

            # ? Auto skip relations
            if field.name in mapper.relationships:
                continue

            # ? Obtain dc value and orm column to compare
            dc_value = getattr(dc_obj, field.name)
            orm_column = mapper.columns.get(field.name)
            if orm_column is None:
                continue

            # ? Validate using provided python type
            if strict_validation and dc_value is not None:
                try:
                    expected_type = orm_column.type.python_type
                except NotImplementedError:
                    pass
                else:
                    if not isinstance(dc_value, expected_type):
                        raise TypeError(
                            f"Field '{field.name}' expects type {expected_type}, "
                            f"got {type(dc_value)}"
                        )

            kwargs[field.name] = dc_value

        return cls(**kwargs)


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="src.db.models.",
    )
    for module in modules:
        __import__(module.name)
