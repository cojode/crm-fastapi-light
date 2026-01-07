from typing import Any
from dataclasses import fields

from typing import Self

from src.logger import logger


class FromObjectMixin:
    @classmethod
    def from_object(
        cls,
        obj: Any,
        convert_relation_fields: list[tuple[str, type]] | None = None,
        **inner_conversions: list[tuple[str, type]],
    ) -> Self:
        """
        Creates an instance of the dataclass from an arbitrary object by mapping its attributes to the dataclass fields.

        Args:
            obj (Any): The source object to convert. If None, returns None.
            convert_relation_fields (list[tuple[str, type]], optional):
                A list of tuples specifying relation field names and their corresponding dataclass types.
                These fields will be recursively converted using their respective `from_object` methods.
            **inner_conversions (list[tuple[str, type]]):
                Additional keyword arguments specifying conversion information for nested relation fields.

        Returns:
            Self | None: An instance of the dataclass populated with values from the source object, or None if the source is None.

        Logs:
            - Logs when the passed object is None.
            - Logs the conversion process and the resulting dataclass instance.
        """
        if obj is None:
            return None
        field_names = {f.name for f in fields(cls)}
        kwargs = {
            name: getattr(obj, name) for name in field_names if hasattr(obj, name)
        }
        if convert_relation_fields is not None:
            for relation_field_name, dataclass_type in convert_relation_fields:
                target = kwargs.get(relation_field_name)
                conversion = inner_conversions.get(relation_field_name)
                kwargs[relation_field_name] = (
                    dataclass_type.from_object(target, conversion)
                    if not isinstance(target, list)
                    else [dataclass_type.from_object(obj, conversion) for obj in target]
                )

        dc = cls(**kwargs)
        logger.debug("Converted object [%s] to the dataclass:\n%s", str(obj), dc)
        return dc
