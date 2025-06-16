# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Iterable, Literal

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays.base.errors import MultipleRecordsReturned, RecordDoesNotExist
from power_grid_model_ds._core.utils.misc import is_sequence


def get_filter_mask(
    *args: int | Iterable[int] | np.ndarray,
    array: np.ndarray,
    mode_: Literal["AND", "OR"],
    **kwargs: Any | list[Any] | np.ndarray,
) -> np.ndarray:
    """Returns a mask that matches the input parameters."""
    parsed_kwargs = _parse(args, kwargs)

    if invalid_kwargs := set(parsed_kwargs.keys()) - set(array.dtype.names or ()):
        raise ValueError(f"Invalid kwargs: {invalid_kwargs}")

    filter_mask = _initialize_filter_mask(mode_, array.size)
    for field, values in parsed_kwargs.items():
        field_mask = _build_filter_mask_for_field(array, field, values)
        if mode_ == "AND":
            filter_mask &= field_mask
        elif mode_ == "OR":
            filter_mask |= field_mask
        else:
            raise ValueError(f"Invalid mode: {mode_}, must be 'AND' or 'OR'")
    return filter_mask


def apply_filter(
    *args: int | Iterable[int] | np.ndarray,
    array: np.ndarray,
    mode_: Literal["AND", "OR"],
    **kwargs: Any | list[Any] | np.ndarray,
) -> np.ndarray:
    """Return an array with the records that match the input parameters.
    Note: output could be an empty array."""
    filter_mask = get_filter_mask(*args, array=array, mode_=mode_, **kwargs)
    return array[filter_mask]


def apply_exclude(
    *args: int | Iterable[int] | np.ndarray,
    array: np.ndarray,
    mode_: Literal["AND", "OR"],
    **kwargs: Any | list[Any] | np.ndarray,
) -> np.ndarray:
    """Return an array without records that match the input parameters.
    Note: output could be an empty array."""
    filter_mask = get_filter_mask(*args, array=array, mode_=mode_, **kwargs)
    return array[~filter_mask]


def apply_get(
    *args: int | Iterable[int] | np.ndarray,
    array: np.ndarray,
    mode_: Literal["AND", "OR"],
    **kwargs: Any | list[Any] | np.ndarray,
) -> np.ndarray:
    """Returns a record that matches the input parameters.
    If no or multiple records match the input parameters, an error is raised.
    """
    filtered_array = apply_filter(*args, array=array, mode_=mode_, **kwargs)
    if filtered_array.size == 1:
        return filtered_array

    args_str = f"\n\twith args: {args[0]}" if args else ""
    kwargs_str = f"\n\twith kwargs: {kwargs}" if kwargs else ""
    if filtered_array.size == 0:
        raise RecordDoesNotExist(f"No record found! {args_str}{kwargs_str}")
    raise MultipleRecordsReturned(f"Found more than one record! {args_str}{kwargs_str}")


def _build_filter_mask_for_field(array: np.ndarray, field: str, values) -> np.ndarray:
    if not is_sequence(values):
        # Note: is_sequence() does not consider a string as a sequence.
        values = [values]

    if not len(values):  # pylint: disable=use-implicit-booleaness-not-len
        return np.full(array.size, False)
    if isinstance(values, set):
        values = list(values)
    if len(values) == 1:  # speed-up for single value
        return array[field] == values[0]
    return np.isin(array[field], values)


def _parse(args: tuple[int | Iterable[int] | NDArray, ...] | NDArray[np.int64], kwargs):
    if not args and not kwargs:
        raise TypeError("No input provided.")
    if len(args) > 1:
        raise ValueError("Cannot parse more than 1 positional argument.")
    if len(args) == 1 and "id" in kwargs:
        raise ValueError("Cannot parse both positional argument and keyword argument 'id'.")
    if len(args) == 1 and isinstance(args[0], int):
        kwargs.update({"id": args})
    elif len(args) == 1:
        kwargs.update({"id": args[0]})
    return kwargs


def _initialize_filter_mask(mode_: Literal["AND", "OR"], size: int) -> np.ndarray:
    if mode_ == "AND":
        return np.full(size, True)
    if mode_ == "OR":
        return np.full(size, False)
    raise ValueError(f"Invalid mode: {mode_}, must be 'AND' or 'OR'")
