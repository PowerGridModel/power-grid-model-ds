from dataclasses import dataclass
from typing import Any, Type

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel


def grid_extension_factory(
    *,
    name: str = "DynamicExtendedGrid",
    graph_model: type[BaseGraphModel] = RustworkxGraphModel,
    user_arrays: dict[str, Type[FancyArray]] | None = None,
    user_fields: dict[str, tuple[type[Any], Any]] | None = None,
) -> tuple[Type[Grid], Grid]:
    """Build a Grid subclass and instantiate it with the provided array and value types."""

    namespace: dict[str, Any] = {
        "__annotations__": dict(user_arrays or {}),
        "__module__": Grid.__module__,
    }

    if user_fields:
        for field_name, field_definition in user_fields.items():
            _apply_user_field(field_name, field_definition, namespace)

    dynamic_grid_cls = dataclass(type(name, (Grid,), namespace))
    return dynamic_grid_cls, dynamic_grid_cls.empty(graph_model=graph_model)


def _apply_user_field(
    field_name: str,
    field_definition: tuple[type[Any], Any],
    namespace: dict[str, Any],
) -> None:
    try:
        field_type, default_value = field_definition
    except (TypeError, ValueError) as error:
        raise TypeError("user_fields must map to (type, default) tuples") from error

    annotations: dict[str, Any] = namespace.setdefault("__annotations__", {})
    annotations[field_name] = field_type
    namespace[field_name] = default_value
