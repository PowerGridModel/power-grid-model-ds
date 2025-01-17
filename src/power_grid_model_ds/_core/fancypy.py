# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""A set of helper functions that mimic numpy functions but are specifically designed for FancyArrays."""

from typing import TYPE_CHECKING, Union

import numpy as np

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.arrays.base.array import FancyArray


def concatenate(fancy_array: "FancyArray", *other_arrays: Union["FancyArray", np.ndarray]) -> "FancyArray":
    """Concatenate arrays."""
    np_arrays = [array if isinstance(array, np.ndarray) else array.data for array in other_arrays]
    try:
        concatenated = np.concatenate([fancy_array.data] + np_arrays)
    except TypeError as error:
        raise TypeError("Cannot append arrays: mismatching dtypes.") from error
    return fancy_array.__class__(data=concatenated)


def unique(array: "FancyArray", **kwargs):
    """Return the unique elements of the array."""
    for column in array.columns:
        if np.issubdtype(array.dtype[column], np.floating) and np.isnan(array[column]).any():
            raise NotImplementedError("Finding unique records in array with NaN values is not supported.")
            # see https://github.com/numpy/numpy/issues/23286
    unique_data = np.unique(array.data, **kwargs)
    if isinstance(unique_data, tuple):
        unique_data, *other = unique_data
        return array.__class__(data=unique_data), *other
    return array.__class__(data=unique_data)


def sort(array: "FancyArray", axis=-1, kind=None, order=None) -> "FancyArray":
    """Sort the array in-place and return sorted array."""
    array.data.sort(axis=axis, kind=kind, order=order)
    return array


def array_equal(array1: "FancyArray", array2: "FancyArray", equal_nan: bool = True) -> bool:
    """Return True if two arrays are equal."""
    if equal_nan:
        return _array_equal_with_nan(array1, array2)
    return np.array_equal(array1.data, array2.data)


def _array_equal_with_nan(array1: "FancyArray", array2: "FancyArray") -> bool:
    # np.array_equal does not work with NaN values in structured arrays, so we need to compare column by column.
    # related issue: https://github.com/numpy/numpy/issues/21539

    if array1.columns != array2.columns:
        return False

    for column in array1.columns:
        column_dtype = array1.dtype[column]
        if np.issubdtype(column_dtype, np.str_):
            if not np.array_equal(array1[column], array2[column]):
                return False
            continue
        if not np.array_equal(array1[column], array2[column], equal_nan=True):
            return False
    return True
