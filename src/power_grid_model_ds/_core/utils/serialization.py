# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Serialization utilities for Grid objects using power-grid-model serialization with extensions support."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid

logger = logging.getLogger(__name__)


def _restore_grid_values(grid, input_data: Dict) -> None:
    """Restore arrays to the grid."""
    for attr_name, attr_values in input_data.items():
        if not hasattr(grid, attr_name):
            continue

        if not issubclass(getattr(grid, attr_name).__class__, FancyArray):
            setattr(grid, attr_name, attr_values)
            continue

        try:
            array_field = grid.find_array_field(getattr(grid, attr_name).__class__)
            matched_columns = {
                col: attr_values["data"][col] for col in array_field.type().columns if col in attr_values["data"]
            }
            restored_array = array_field.type(**matched_columns)
            setattr(grid, attr_name, restored_array)
        except (AttributeError, KeyError, ValueError, TypeError) as e:
            # Handle restoration failures:
            # - KeyError: missing "dtype" or "data" keys
            # - ValueError/TypeError: invalid dtype string or data conversion
            # - AttributeError: grid methods/attributes missing
            logger.warning(f"Failed to restore '{attr_name}': {e}")


def save_grid_to_json(
    grid,
    path: Path,
    indent: Optional[int] = None,
) -> Path:
    """Save a Grid object to JSON format using power-grid-model serialization with extensions support.

    Args:
        grid: The Grid object to serialize
        path: The file path to save to
        indent: JSON indentation (None for compact, positive int for indentation)
    Returns:
        Path: The path where the file was saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    serialized_data = {}
    for field in dataclasses.fields(grid):
        if field.name in ["graphs", "_id_counter"]:
            continue

        field_value = getattr(grid, field.name)
        if isinstance(field_value, (int, float, str, bool)):
            serialized_data[field.name] = field_value

        if not isinstance(field_value, FancyArray) or field_value.size == 0:
            continue

        serialized_data[field.name] = {
            "data": {name: field_value[name].tolist() for name in field_value.dtype.names},
        }

    # Write to file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialized_data, f, indent=indent if indent and indent > 0 else None)

    return path


def load_grid_from_json(path: Path, target_grid_class=None):
    """Load a Grid object from JSON format with cross-type loading support.

    Args:
        path: The file path to load from
        target_grid_class: Optional Grid class to load into. If None, uses default Grid.

    Returns:
        Grid: The deserialized Grid object of the specified target class
    """
    with open(path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    if target_grid_class is None:
        target_grid = Grid.empty()
    else:
        target_grid = target_grid_class.empty()

    _restore_grid_values(target_grid, input_data)

    return target_grid
