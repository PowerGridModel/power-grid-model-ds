# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""A set of helper functions that mimic numpy functions but are specifically designed for FancyArrays."""

from typing import TYPE_CHECKING, TypeVar, Union

import numpy as np

from power_grid_model_ds._core.utils.misc import array_equal_with_nan

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.arrays.base.array import FancyArray

T = TypeVar("T", bound="FancyArray")


def concatenate(fancy_array: T, *other_arrays: Union[T, np.ndarray]) -> T:
    """Concatenate arrays."""
    np_arrays = [array if isinstance(array, np.ndarray) else array.data for array in other_arrays]
    try:
        concatenated = np.concatenate([fancy_array.data] + np_arrays)
    except TypeError as error:
        raise TypeError("Cannot append arrays: mismatching dtypes.") from error
    return fancy_array.__class__(data=concatenated)


def unique(array: T, **kwargs):
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


def sort(array: T, axis=-1, kind=None, order=None) -> T:
    """Sort the array in-place and return sorted array."""
    array.data.sort(axis=axis, kind=kind, order=order)
    return array


def array_equal(array1: T, array2: T, equal_nan: bool = True) -> bool:
    """Return True if two arrays are equal."""
    if equal_nan:
        return array_equal_with_nan(array1.data, array2.data)
    return np.array_equal(array1.data, array2.data)
