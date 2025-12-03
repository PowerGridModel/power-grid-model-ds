# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Serialization utilities for Grid objects using power-grid-model serialization with extensions support."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Type, TypeVar

from power_grid_model_ds._core.model.arrays.base.array import FancyArray

if TYPE_CHECKING:
    # Import only for type checking to avoid circular imports at runtime
    from power_grid_model_ds._core.model.grids.base import Grid

    G = TypeVar("G", bound=Grid)
else:
    # Runtime: don't import Grid to avoid circular import; keep unbound TypeVar
    G = TypeVar("G")

logger = logging.getLogger(__name__)


def save_grid_to_json(grid, path: Path, strict: bool = True, **kwargs) -> Path:
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
        if field.name in ["graphs", "_id_counter"]:
            continue

        field_value = getattr(grid, field.name)

        if isinstance(field_value, FancyArray):
            serialized_data[field.name] = {
                "data": {name: field_value[name].tolist() for name in field_value.dtype.names},
            }
            continue

        if _is_serializable(field_value, strict):
            serialized_data[field.name] = field_value

    # Write to file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialized_data, f, **kwargs)

    return path


def load_grid_from_json(path: Path, target_grid_class: Type[G]) -> G:
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
            if extra := set(attr_values["data"]) - set(grid_attr.columns):
                logger.warning(f"{attr_name} has extra columns: {extra}")

            matched_columns = {col: attr_values["data"][col] for col in grid_attr.columns if col in attr_values["data"]}
            restored_array = attr_class(**matched_columns)
            setattr(grid, attr_name, restored_array)
            continue

        # load other values
        setattr(grid, attr_name, attr_class(attr_values))


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
