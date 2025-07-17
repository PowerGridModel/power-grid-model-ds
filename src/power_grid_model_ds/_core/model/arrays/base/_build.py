# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Contains the build_array function."""

import logging
from collections.abc import Sized
from typing import Any, Iterable

import numpy as np

from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.utils.misc import is_sequence


def build_array(*args: tuple[Any], dtype: np.dtype, defaults: dict[str, np.generic], **kwargs) -> np.ndarray:
    """Constructs the array from the given args/kwargs."""
    parsed_input, size = _parse_input(*args, dtype=dtype, **kwargs)

    array: np.ndarray = np.zeros(size, dtype=dtype)
    _fill_defaults(array, defaults)

    if not size:
        return array

    if isinstance(parsed_input, np.ndarray) and parsed_input.dtype.names:
        _check_missing_columns(array.dtype.names or (), defaults, set(parsed_input.dtype.names))
        return _parse_structured_array(parsed_input, array)
    if isinstance(parsed_input, np.ndarray):
        # Note: defaults are not supported when working with unstructured arrays
        return _parse_array(parsed_input, array.dtype)

    _check_missing_columns(array.dtype.names or (), defaults, set(parsed_input.keys()))
    _fill_with_kwargs(array, parsed_input)
    return array


def _parse_input(*args: Any, dtype: np.dtype, **kwargs):
    """Combines the args and kwargs to a dict."""
    columns: list[str] = list(dtype.names) if dtype.names else []
    if args and kwargs:
        raise TypeError("Cannot construct from both args and kwargs")

    if args and isinstance(args[0], np.ndarray):
        return args[0], len(args[0])
    if args and isinstance(args[0], Iterable):
        kwargs = _args2kwargs(args, columns)
    elif args:
        raise TypeError(f"Invalid args: {args}")

    if kwargs:
        return _parse_kwargs(kwargs, columns)
    return {}, 0


def _check_missing_columns(array_columns: tuple[str, ...], defaults: dict[str, np.generic], provided_columns: set[str]):
    required_columns = set(array_columns) - set(defaults.keys())
    if missing_columns := required_columns - provided_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def _fill_defaults(array: np.ndarray, defaults: dict[str, np.generic]):
    """Fills the defaults into the array."""
    for column, default in defaults.items():
        if default is empty:
            column_type: type = array.dtype[column]
            array[column] = empty(column_type)  # type: ignore[call-overload]
        else:
            array[column] = default  # type: ignore[call-overload]


def _fill_with_kwargs(array: np.ndarray, kwargs: dict[str, np.ndarray]):
    """Fills the kwargs into the array."""
    for column, values in kwargs.items():
        array[column] = values  # type: ignore[call-overload]


def _parse_structured_array(from_array: np.ndarray, to_array: np.ndarray) -> np.ndarray:
    shared_columns, ignored_columns = _determine_column_overlap(from_array, to_array)
    if ignored_columns:
        logging.debug(
            "Ignored provided columns %s during build of array with columns %s", ignored_columns, to_array.dtype.names
        )
    to_array[shared_columns] = from_array[shared_columns]  # type: ignore[index]
    return to_array


def _determine_column_overlap(from_array: np.ndarray, to_array: np.ndarray) -> tuple[list[str], list[str]]:
    """Returns two lists: columns present in both arrays and the columns that are only present in from_array"""
    from_columns = set(from_array.dtype.names or ())
    to_columns = set(to_array.dtype.names or ())

    return list(from_columns & to_columns), list(from_columns - to_columns)


def _parse_array(array: np.ndarray, dtype: np.dtype):
    if len(array.shape) == 1 and array.dtype == dtype:
        return array
    if len(array.shape) == 1:
        return np.array(array, dtype=dtype)
    if len(array.shape) == 2:
        return _parse_2d_array(array, dtype)
    raise NotImplementedError(f"Unsupported array shape {array.shape}")


def _parse_2d_array(array: np.ndarray, dtype: np.dtype):
    """Parses the 2d array to a 1d array."""
    columns: list[str] = list(dtype.names) if dtype.names else []
    if len(columns) not in array.shape:
        raise ValueError(f"Cannot convert array of shape {array.shape} into {len(columns)} columns.")
    column_dim = 0 if len(columns) == array.shape[0] else 1
    size_dim = 1 if column_dim == 0 else 0
    new_array = np.ones(array.shape[size_dim], dtype=dtype)
    for index, column in enumerate(columns):
        if column_dim == 0:
            new_array[column] = array[index, :]  # type: ignore[call-overload]
        else:
            new_array[column] = array[:, index]  # type: ignore[call-overload]
    return new_array


def _parse_kwargs(kwargs: dict[str, list | np.ndarray], columns: list[str]) -> tuple[dict[str, np.ndarray], int]:
    """Parses the kwargs to a dict of np.ndarrays."""
    parsed_kwargs = {}

    size = 0
    for column, values in kwargs.items():
        parsed_kwargs[column] = np.array(values).flatten()

        value_size = _get_size(values)
        if size == 0:
            size = value_size
        elif size != len(values):
            raise ValueError(f"Size of column '{column}' does not match other columns.")

    if invalid_columns := set(parsed_kwargs.keys()) - set(columns):
        raise ValueError(f"Invalid columns: {invalid_columns}")
    return parsed_kwargs, size


def _get_size(values: Sized):
    """Returns the size of the values."""
    if is_sequence(values):
        return len(values)
    return 1


def _args2kwargs(args: tuple[Any, ...], columns: list[str]) -> dict[str, list]:
    """Parses the args to kwargs."""
    kwargs = {}
    if len(args) == 1:
        args = args[0]

    args_as_array = np.array(args)
    if len(args_as_array.shape) != 2:
        raise ValueError(
            "Cannot parse args: input is not 2D, probably due to an inconsistent number of values per row."
        )

    _, args_n_columns = args_as_array.shape
    if args_n_columns != len(columns):
        raise ValueError(f"Cannot parse args: requires {len(columns)} columns per row, got {args_n_columns}.")

    for index, column in enumerate(columns):
        kwargs[column] = [row[index] for row in args]
    return kwargs
