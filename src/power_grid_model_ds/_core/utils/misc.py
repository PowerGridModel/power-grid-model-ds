# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Misc utils"""

from collections.abc import Sequence
from typing import Type, get_type_hints

import numpy as np


def is_sequence(seq):
    """
    Returns True for lists, tuples, sets, arrays
    Return False for strings, dicts
    """
    if isinstance(seq, str):
        return False

    if isinstance(seq, (np.ndarray, set)):
        return True
    return isinstance(seq, Sequence)


def get_inherited_attrs(cls: Type, *private_attributes):
    """
    Get the attribute from the object and all its parents
    """

    # The extras are needed for annotated types like NDArray3
    retrieved_attributes = get_type_hints(cls, include_extras=True)
    retrieved_attributes = {attr: type for attr, type in retrieved_attributes.items() if not attr.startswith("_")}

    for private_attr in private_attributes:
        for parent in reversed(list(cls.__mro__)):
            attr_dict = retrieved_attributes.get(private_attr, {})
            attr_dict.update(getattr(parent, private_attr, {}))
            retrieved_attributes[private_attr] = attr_dict

    return retrieved_attributes


def array_equal_with_nan(array1: np.ndarray, array2: np.ndarray) -> bool:
    """Compare two structured arrays for equality, treating NaN values as equal.

    np.array_equal does not work with NaN values in structured arrays, so we need to compare column by column.
    related issue: https://github.com/numpy/numpy/issues/21539
    """
    if array1.dtype.names != array2.dtype.names:
        return False

    columns: Sequence[str] = array1.dtype.names
    for column in columns:
        column_dtype = array1.dtype[column]
        if np.issubdtype(column_dtype, np.str_):
            if not np.array_equal(array1[column], array2[column]):
                return False
            continue
        if not np.array_equal(array1[column], array2[column], equal_nan=True):
            return False
    return True


def find_diff_masks_with_equal_nan(array1: np.ndarray, array2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the rows in array1 that are not in array2, treating NaN values as equal."""
    if array1.dtype != array2.dtype:
        raise TypeError("Cannot find differences. Arrays must have the same dtypes.")

    if array1.size == 0 and array2.size == 0:
        return np.zeros(0, dtype=bool), np.zeros(0, dtype=bool)

    # copy arrays, since we are potentially modifying them by replacing NaN values with np.inf
    inf_array1 = array1.copy()
    inf_array2 = array2.copy()

    for column in array1.dtype.names:  # type: ignore[arg-type,union-attr]
        nan_mask_1 = np.isnan(array1[column])
        nan_mask_2 = np.isnan(array2[column])
        if nan_mask_1.any() or nan_mask_2.any():
            inf_array1[column][nan_mask_1] = np.inf
            inf_array2[column][nan_mask_2] = np.inf

    array1_diff_mask = np.isin(inf_array1, inf_array2, invert=True)
    array2_diff_mask = np.isin(inf_array2, inf_array1, invert=True)
    return array1_diff_mask, array2_diff_mask
