# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Serialization utilities for Grid objects using power-grid-model serialization with extensions support."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.serialization.errors import JSONDeserializationError, JSONSerializationError

if TYPE_CHECKING:
    # Import only for type checking to avoid circular imports at runtime
    from power_grid_model_ds._core.model.grids.base import Grid


G = TypeVar("G", bound="Grid")


logger = logging.getLogger(__name__)


def serialize_to_json(grid: G, path: Path, strict: bool = True, **kwargs) -> Path:
    """Save a Grid object to JSON format using power-grid-model serialization with extensions support.

    Args:
        grid: The Grid object to serialize
        path: The file path to save to
        strict: Whether to raise an error if the grid object is not serializable.
        **kwargs: Keyword arguments forwarded to json.dump (for example, indent, sort_keys,
            ensure_ascii, etc.).
    Returns:
        Path: The path where the file was saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    serialized_data = {}

    for field in dataclasses.fields(grid):
        if field.name in ["graphs"]:
            continue

        field_value = getattr(grid, field.name)

        if isinstance(field_value, FancyArray):
            serialized_data[field.name] = _serialize_array(field_value)
            continue

        if hasattr(field_value, "to_dict"):
            field_value = field_value.to_dict()

        if _is_serializable(field_value, strict):
            serialized_data[field.name] = field_value

    # Store in a wrapper for PGM compatibility
    json_data = {"data": serialized_data}

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, **kwargs)

    return path


def deserialize_from_json(path: Path, target_grid_class: type[G], strict: bool = True) -> G:
    """Load a Grid object from JSON format with cross-type loading support.

    Args:
        path: The file path to load from
        target_grid_class: Grid class to load into.
        strict: Whether to raise an error if the grid object cannot be fully restored.

    Returns:
        Grid: The deserialized Grid object of the specified target class
    """
    with open(path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    grid = target_grid_class.empty()
    _restore_grid_values(grid, json_data["data"], strict=strict)
    graph_class = grid.graphs.__class__
    grid.graphs = graph_class.from_arrays(grid)
    return grid


def _restore_grid_values(grid: G, json_data: dict, strict: bool) -> None:
    """Restore arrays to the grid."""
    for attr_name, attr_values in json_data.items():
        if not hasattr(grid, attr_name):
            logger.warning(f"Unexpected attribute '{attr_name}'")
            continue

        grid_attr = getattr(grid, attr_name)
        attr_class = grid_attr.__class__
        if isinstance(grid_attr, FancyArray):
            array = _deserialize_array(array_data=attr_values, array_class=attr_class)
            setattr(grid, attr_name, array)
            continue
        if hasattr(grid_attr, "from_dict"):
            attr_value = grid_attr.from_dict(attr_values)
            setattr(grid, attr_name, attr_value)
            continue

        try:
            setattr(grid, attr_name, attr_class(attr_values))
        except TypeError as error:
            msg = f"Failed to set attribute '{attr_name}' on grid of type '{grid.__class__.__name__}'."
            if strict:
                msg += " Set strict=False to skip it or add a .from_dict() class method to the attribute's class."
                raise JSONDeserializationError(msg) from error
            logger.warning(msg)


def _serialize_array(array: FancyArray) -> list[dict[str, Any]]:
    return [{name: record[name].item() for name in array.columns} for record in array]


def _deserialize_array(array_data: list[dict[str, Any]], array_class: type[FancyArray]) -> FancyArray:
    if not array_data:
        return array_class()

    array_columns = set(array_class.get_dtype().names)

    data_as_dict_of_lists: dict[str, Any] = {}
    for column in array_columns:
        column_data = [row[column] for row in array_data if column in row]
        if len(column_data) not in [0, len(array_data)]:
            raise ValueError(
                f"Some records in column '{column}' have missing values. "
                f"For defaulted columns, either provide all values or none."
            )
        if column_data:
            data_as_dict_of_lists[column] = column_data

    all_columns_in_array_data = set().union(*(row.keys() for row in array_data))
    extra_columns = all_columns_in_array_data - array_columns
    if extra_columns:
        logger.warning(f"Ignoring extra columns {extra_columns} from array data for {array_class.__name__}.")
    return array_class(**data_as_dict_of_lists)


def _is_serializable(value: Any, strict: bool) -> bool:
    # Check if a value is JSON serializable.
    try:
        json.dumps(value)
    except TypeError as error:
        msg = f"Failed to serialize '{value.__class__.__name__}'. "
        if strict:
            msg += "Set strict=False to skip this attribute or add a .to_dict() method to the attribute's class."
            raise JSONSerializationError(msg) from error
        logger.warning(msg)
        return False
    return True
