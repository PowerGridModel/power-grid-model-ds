# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Serialization utilities for Grid objects using power-grid-model serialization with extensions support."""

import dataclasses
import json
import logging
from ast import literal_eval
from pathlib import Path
from typing import Dict, Literal, Optional

import msgpack
import numpy as np
from power_grid_model.utils import json_deserialize, json_serialize, msgpack_deserialize, msgpack_serialize

from power_grid_model_ds._core.load_flow import PGM_ARRAYS, PowerGridModelInterface
from power_grid_model_ds._core.model.arrays.base.array import FancyArray

# Constants
EXTENDED_COLUMNS_KEY = "extended_columns"
CUSTOM_ARRAYS_KEY = "custom_arrays"
EXTENSIONS_KEY = "pgm_ds_extensions"

logger = logging.getLogger(__name__)


def _extract_extensions_data(grid) -> Dict[str, Dict]:
    """Extract extended columns and non-PGM arrays from a Grid object.

    Args:
        grid: The Grid object

    Returns:
        Dict containing extensions data with keys EXTENDED_COLUMNS_KEY and CUSTOM_ARRAYS_KEY
    """
    extensions: dict = {EXTENDED_COLUMNS_KEY: {}, CUSTOM_ARRAYS_KEY: {}}

    for field in dataclasses.fields(grid):
        if field.name in ["graphs", "_id_counter"]:
            continue

        array = getattr(grid, field.name)
        if not isinstance(array, FancyArray) or array.size == 0:
            continue

        array_name = field.name

        if array_name in PGM_ARRAYS:
            # Extract extended columns for PGM arrays
            _extract_extended_columns(grid, array_name, array, extensions)
        else:
            # Store custom arrays not in PGM_ARRAYS
            extensions[CUSTOM_ARRAYS_KEY][array_name] = {"dtype": str(array.dtype), "data": array.data.tolist()}

    return extensions


def _extract_extended_columns(grid, array_name: str, array: FancyArray, extensions: Dict) -> None:
    """Extract extended columns from a PGM array."""
    try:
        interface = PowerGridModelInterface(grid=grid)
        # pylint: disable=protected-access  # Accessing internal method for extension extraction
        pgm_array = interface._create_power_grid_array(array_name)
        pgm_columns = set(pgm_array.dtype.names or [])
        ds_columns = set(array.columns)

        # Find extended columns (columns in DS but not in PGM)
        extended_cols = ds_columns - pgm_columns
        if extended_cols:
            extensions[EXTENDED_COLUMNS_KEY][array_name] = {col: array[col].tolist() for col in extended_cols}
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        # Handle various failure modes:
        # - KeyError: array_name not found in PGM arrays
        # - AttributeError: array missing dtype/columns or interface method missing
        # - TypeError/ValueError: invalid array configuration or data conversion issues
        logger.warning(f"Failed to extract extensions for array '{array_name}': {e}")
        extensions[CUSTOM_ARRAYS_KEY][array_name] = {"dtype": str(array.dtype), "data": array.data.tolist()}


def _restore_extensions_data(grid, extensions_data: Dict) -> None:
    """Restore extended columns and custom arrays to a Grid object.

    Args:
        grid: The Grid object to restore extensions to
        extensions_data: Extensions data from _extract_extensions_data
    """
    # Restore extended columns
    _restore_extended_columns(grid, extensions_data.get(EXTENDED_COLUMNS_KEY, {}))

    # Restore custom arrays
    _restore_custom_arrays(grid, extensions_data.get(CUSTOM_ARRAYS_KEY, {}))


def _restore_extended_columns(grid, extended_columns: Dict) -> None:
    """Restore extended columns to existing arrays."""
    for array_name, extended_cols in extended_columns.items():
        if not hasattr(grid, array_name):
            logger.warning(f"Grid has no attribute '{array_name}' to restore")
            continue

        array = getattr(grid, array_name)
        if not isinstance(array, FancyArray) or array.size == 0:
            continue

        for col_name, values in extended_cols.items():
            # if hasattr(array, col_name):
            try:
                array[col_name] = values
            except (AttributeError, IndexError, ValueError, TypeError) as e:
                # Handle assignment failures:
                # - IndexError: array size mismatch
                # - ValueError/TypeError: incompatible data types
                # - AttributeError: array doesn't support assignment
                logger.warning(f"Failed to restore column '{col_name}' in array '{array_name}': {e}")


def _parse_dtype(dtype_str: str) -> np.dtype:
    """Parse a dtype string into a numpy dtype."""
    if not isinstance(dtype_str, str):
        raise ValueError(f"Invalid dtype string: {dtype_str}")

    # Use numpy's dtype parsing - handle both eval-style and direct strings
    if dtype_str.startswith("dtype("):
        clean_dtype_str = dtype_str.replace("dtype(", "").replace(")", "")
    else:
        clean_dtype_str = dtype_str

    # Use eval for complex dtype strings like "[('field', 'type'), ...]"
    if clean_dtype_str.startswith("[") and clean_dtype_str.endswith("]"):
        return np.dtype(literal_eval(clean_dtype_str))
    return np.dtype(clean_dtype_str)


def _construct_numpy_from_list(raw_data, dtype: np.dtype) -> np.ndarray:
    """Construct a numpy array from a list with the specified dtype."""
    if dtype.names:  # Structured dtype
        # Convert from list of lists to list of tuples for structured array
        if isinstance(raw_data[0], (list, tuple)) and len(raw_data[0]) == len(dtype.names):
            data = np.array([tuple(row) for row in raw_data], dtype=dtype)
        else:
            data = np.array(raw_data, dtype=dtype)
    else:
        data = np.array(raw_data, dtype=dtype)
    return data


def _restore_custom_arrays(grid, custom_arrays: Dict) -> None:
    """Restore custom arrays to the grid."""
    for array_name, array_info in custom_arrays.items():
        if not hasattr(grid, array_name):
            continue

        try:
            dtype = _parse_dtype(dtype_str=array_info["dtype"])
            data = _construct_numpy_from_list(array_info["data"], dtype)
            array_field = grid.find_array_field(getattr(grid, array_name).__class__)
            restored_array = array_field.type(data=data)
            setattr(grid, array_name, restored_array)
        except (AttributeError, KeyError, ValueError, TypeError) as e:
            # Handle restoration failures:
            # - KeyError: missing "dtype" or "data" keys
            # - ValueError/TypeError: invalid dtype string or data conversion
            # - AttributeError: grid methods/attributes missing
            logger.warning(f"Failed to restore custom array '{array_name}': {e}")


def _create_grid_from_input_data(input_data: Dict, target_grid_class=None):
    """Create a Grid object from power-grid-model input data.

    Args:
        input_data: Power-grid-model input data
        target_grid_class: Optional Grid class to create. If None, uses default Grid.

    Returns:
        Grid object populated with the input data
    """
    if target_grid_class is not None:
        # Create empty grid of target type and populate it with input data
        target_grid = target_grid_class.empty()
        interface = PowerGridModelInterface(grid=target_grid, input_data=input_data)
        return interface.create_grid_from_input_data()

    # Use default Grid type
    interface = PowerGridModelInterface(input_data=input_data)
    return interface.create_grid_from_input_data()


def _extract_msgpack_data(data: bytes, **kwargs):
    """Extract input data and extensions from MessagePack data."""
    try:
        data_dict = msgpack.unpackb(data, raw=False)
        if isinstance(data_dict, dict) and EXTENSIONS_KEY in data_dict:
            # Extract extensions and deserialize core data
            extensions = data_dict.pop(EXTENSIONS_KEY, {})
            core_data = msgpack.packb(data_dict)
            input_data = msgpack_deserialize(core_data, **kwargs)
        else:
            # No extensions, use power-grid-model directly
            input_data = msgpack_deserialize(data, **kwargs)
            extensions = {EXTENDED_COLUMNS_KEY: {}, CUSTOM_ARRAYS_KEY: {}}
    except (msgpack.exceptions.ExtraData, ValueError, TypeError) as e:
        # Handle MessagePack parsing failures:
        # - ExtraData: malformed MessagePack data
        # - ValueError/TypeError: invalid data structure or type issues
        logger.warning(f"Failed to extract extensions from MessagePack data: {e}")
        input_data = msgpack_deserialize(data, **kwargs)
        extensions = {EXTENDED_COLUMNS_KEY: {}, CUSTOM_ARRAYS_KEY: {}}

    return input_data, extensions


def _get_serialization_path(path: Path, format_type: Literal["json", "msgpack", "auto"] = "auto") -> Path:
    """Get the correct path for serialization format.

    Args:
        path: Base path
        format_type: "json", "msgpack", or "auto" to detect from extension

    Returns:
        Path: Path with correct extension
    """
    JSON_EXTENSIONS = [".json"]
    MSGPACK_EXTENSIONS = [".msgpack", ".mp"]

    if format_type == "auto":
        if path.suffix.lower() in JSON_EXTENSIONS:
            format_type = "json"
        elif path.suffix.lower() in MSGPACK_EXTENSIONS:
            format_type = "msgpack"
        else:
            # Default to JSON
            format_type = "json"

    if format_type == "json" and path.suffix.lower() != JSON_EXTENSIONS[0]:
        return path.with_suffix(JSON_EXTENSIONS[0])
    if format_type == "msgpack" and path.suffix.lower() not in MSGPACK_EXTENSIONS:
        return path.with_suffix(MSGPACK_EXTENSIONS[0])

    return path


def save_grid_to_json(
    grid,
    path: Path,
    use_compact_list: bool = True,
    indent: Optional[int] = None,
    preserve_extensions: bool = True,
) -> Path:
    """Save a Grid object to JSON format using power-grid-model serialization with extensions support.

    Args:
        grid: The Grid object to serialize
        path: The file path to save to
        use_compact_list: Whether to use compact list format
        indent: JSON indentation (None for compact, positive int for indentation)
        preserve_extensions: Whether to save extended columns and custom arrays
    Returns:
        Path: The path where the file was saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Grid to power-grid-model input format and serialize
    interface = PowerGridModelInterface(grid=grid)
    input_data = interface.create_input_from_grid()

    core_data = json_serialize(input_data, use_compact_list=use_compact_list)

    # Parse and add extensions if requested
    serialized_data = json.loads(core_data)
    if preserve_extensions:
        extensions = _extract_extensions_data(grid)
        if extensions[EXTENDED_COLUMNS_KEY] or extensions[CUSTOM_ARRAYS_KEY]:
            serialized_data[EXTENSIONS_KEY] = extensions

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
        data = json.load(f)

    # Extract extensions and deserialize core data
    extensions = data.pop(EXTENSIONS_KEY, {EXTENDED_COLUMNS_KEY: {}, CUSTOM_ARRAYS_KEY: {}})
    input_data = json_deserialize(json.dumps(data))

    # Create grid and restore extensions
    grid = _create_grid_from_input_data(input_data, target_grid_class)
    _restore_extensions_data(grid, extensions)

    return grid


def save_grid_to_msgpack(grid, path: Path, use_compact_list: bool = True, preserve_extensions: bool = True) -> Path:
    """Save a Grid object to MessagePack format with extensions support.

    Args:
        grid: The Grid object to serialize
        path: The file path to save to
        use_compact_list: Whether to use compact list format
        preserve_extensions: Whether to save extended columns and custom arrays

    Returns:
        Path: The path where the file was saved
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Grid to power-grid-model input format and serialize
    interface = PowerGridModelInterface(grid=grid)
    input_data = interface.create_input_from_grid()

    core_data = msgpack_serialize(input_data, use_compact_list=use_compact_list)

    # Add extensions if requested (requires re-serialization for MessagePack)
    if preserve_extensions:
        extensions = _extract_extensions_data(grid)
        if extensions[EXTENDED_COLUMNS_KEY] or extensions[CUSTOM_ARRAYS_KEY]:
            core_dict = msgpack.unpackb(core_data, raw=False)
            core_dict[EXTENSIONS_KEY] = extensions
            serialized_data = msgpack.packb(core_dict)
        else:
            serialized_data = core_data
    else:
        serialized_data = core_data

    # Write to file
    with open(path, "wb") as f:
        f.write(serialized_data)

    return path


def load_grid_from_msgpack(path: Path, target_grid_class=None):
    """Load a Grid object from MessagePack format with cross-type loading support.

    Args:
        path: The file path to load from
        target_grid_class: Optional Grid class to load into. If None, uses default Grid.

    Returns:
        Grid: The deserialized Grid object of the specified target class
    """
    with open(path, "rb") as f:
        data = f.read()

    # Extract extensions and deserialize core data
    input_data, extensions = _extract_msgpack_data(data)

    # Create grid and restore extensions
    grid = _create_grid_from_input_data(input_data, target_grid_class)
    _restore_extensions_data(grid, extensions)

    return grid
