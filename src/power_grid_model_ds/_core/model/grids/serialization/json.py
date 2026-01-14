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

        if _is_serializable(field_value, strict):
            serialized_data[field.name] = field_value

    # Write to file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialized_data, f, **kwargs)

    return path


def deserialize_from_json(path: Path, target_grid_class: type[G]) -> G:
    """Load a Grid object from JSON format with cross-type loading support.

    Args:
        path: The file path to load from
        target_grid_class: Grid class to load into.

    Returns:
        Grid: The deserialized Grid object of the specified target class
    """
    with open(path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    grid = target_grid_class.empty()
    _restore_grid_values(grid, input_data)
    graph_class = grid.graphs.__class__
    grid.graphs = graph_class.from_arrays(grid)
    return grid


def _restore_grid_values(grid: G, json_data: dict) -> None:
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

        # load other values
        setattr(grid, attr_name, attr_class(attr_values))


def _serialize_array(array: FancyArray) -> list[dict[str, Any]]:
    return [{name: record[name].item() for name in array.columns} for record in array]


def _deserialize_array(array_data: list[dict[str, Any]], array_class: type[FancyArray]) -> FancyArray:
    if not array_data:
        return array_class()

    columns = array_data[0].keys()
    data_as_dict_of_lists: dict[str, Any] = {k: [d[k] for d in array_data] for k in columns}
    array_columns = set(array_class.get_dtype().names)
    if extra := set(data_as_dict_of_lists.keys()) - array_columns:
        logger.warning(f"Skipping extra columns from input data for {array_class.__name__}: {extra}")
    matched_columns = {col: data_as_dict_of_lists[col] for col in array_columns if col in data_as_dict_of_lists}
    return array_class(**matched_columns)


def _is_serializable(value: Any, strict: bool) -> bool:
    # Check if a value is JSON serializable.
    try:
        json.dumps(value)
    except TypeError as error:
        msg = f"Failed to serialize '{value}'. You can set strict=False to ignore this attribute."
        if strict:
            raise TypeError(msg) from error
        logger.warning(msg)
        return False
    return True
