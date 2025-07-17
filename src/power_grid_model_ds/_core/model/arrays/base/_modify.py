# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper functions for arrays"""

import numpy as np
from numpy.typing import ArrayLike, NDArray


def re_order(array: np.ndarray, new_order: ArrayLike, column: str = "id") -> np.ndarray:
    """Re-order an id-array by the id column so that it follows a new_order.
    Expects the new_order input to contain the same values as self.id
    """
    if column not in (array.dtype.names or ()):
        raise ValueError(f"Cannot re-order array: column {column} does not exist.")
    if not np.array_equal(np.sort(array[column]), np.sort(new_order)):
        raise ValueError(f"Cannot re-order array: mismatch between new_order and values in '{column}'-column.")

    permutation_a = np.argsort(array[column])
    permutation_b = np.argsort(new_order)
    inverse = np.empty_like(new_order, dtype=int)
    inverse[permutation_b] = np.arange(permutation_b.size)
    new_order_indices = permutation_a[inverse]
    return array[new_order_indices]


def update_by_id(array: np.ndarray, ids: ArrayLike, allow_missing: bool, **kwargs) -> NDArray[np.bool_]:
    """Update values in an array by id

    Args:
        array: the array to update
        ids: the ids to update
        allow_missing: whether to allow ids that do not exist in the array
        **kwargs: the columns to update and their new values
    Returns:
        mask: the mask on the original array for the provided ids
    """
    mask = np.isin(array["id"], ids)
    if not allow_missing:
        nr_hits = np.sum(mask)
        nr_ids = np.unique(ids).size  # ignore edge cases with duplicate ids
        if nr_hits != nr_ids:
            raise ValueError("One or more ids do not exist. Provide allow_missing=True if this is intended.")

    for name, values in kwargs.items():
        array[name][mask] = values
    return mask


def check_ids(array: np.ndarray, return_duplicates: bool = False) -> NDArray | None:
    """Check for duplicate ids within the array"""
    if "id" not in (array.dtype.names or ()):
        raise AttributeError("Array has no 'id' column.")

    unique, counts = np.unique(array["id"], return_counts=True)
    duplicate_mask = counts > 1
    duplicates = unique[duplicate_mask]

    if return_duplicates:
        return duplicates
    if duplicates.size > 0:
        raise ValueError(f"Found duplicate ids in array: {duplicates}")
    return None
