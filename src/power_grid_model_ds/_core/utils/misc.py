# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Misc utils"""

from collections.abc import Sequence
from typing import get_type_hints

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


def get_public_annotations(cls: type):
    """Get the public annotations for a class"""
    # Note: include_extras=True for annotated types like NDArray3
    class_attributes = get_type_hints(cls, include_extras=True)
    return {attr: type_ for attr, type_ in class_attributes.items() if not attr.startswith("_")}


def build_mro_attribute(cls: type, attribute_name: str, attribute_type: type[dict] | type[set]) -> dict | set:
    """Combine all versions of an attribute in the Method Resolution Order (mro) of a class into a single attribute

    For dicts this means the dict is updated so that child classes override parent classes.
    For sets this means the sets are unioned together.

    Types other than dict and set are not supported
    """
    attr_value = attribute_type()
    for parent in reversed(list(cls.__mro__)):
        if attribute_type is dict:
            attr_value.update(getattr(parent, attribute_name, {}))
        elif attribute_type is set:
            attr_value |= getattr(parent, attribute_name, set())
        else:
            raise NotImplementedError(
                f"Type {attribute_type} cannot combine inherited for attribute {attribute_name}. "
                f"Only dict and set are currently supported."
            )
    return attr_value


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
