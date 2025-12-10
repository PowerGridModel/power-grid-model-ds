# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from dataclasses import fields
from typing import TYPE_CHECKING

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.utils.misc import array_equal_with_nan, logger

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import FancyArrayContainer


def container_equal(
    container_a: "FancyArrayContainer",
    container_b: "FancyArrayContainer",
    ignore_extras: bool = False,
    early_exit: bool = True,
    ignore: list[str] = None,
) -> bool:
    """
    Args:
        container_a(FancyArrayContainer): the other container to compare with.
        container_b(FancyArrayContainer): the container to compare.
        ignore_extras(bool): whether to ignore fields that are only present in `other`.
        early_exit(bool): whether to stop checking upon finding the first difference.
        ignore(list[str]): list of field names to ignore during comparison.
    Returns:
        bool: True if the containers are equal, False otherwise.


    """
    ignore = ignore or []

    class_name = container_a.__class__.__name__
    is_equal = True
    for field in fields(container_a):
        if field.name in ignore:
            continue

        if ignore_extras and not hasattr(container_b, field.name):
            continue

        value_a = getattr(container_a, field.name)
        value_b = getattr(container_b, field.name)

        if isinstance(value_a, FancyArray):
            arrays_are_equal = _check_array_equal(value_a, value_b, ignore_extras)
            if not arrays_are_equal:
                logger.debug(f"Array field '{field.name}' differs between {class_name}s.")
                is_equal = False
                if early_exit:
                    return False

        else:
            if value_a != value_b:
                logger.debug(f"Array field '{field.name}' differs between {class_name}s.")
                is_equal = False
                if early_exit:
                    return False

    if not ignore_extras:
        extra_fields_b = set({field.name for field in fields(container_b)}) - set(
            {field.name for field in fields(container_a)}
        )
        if extra_fields_b:
            logger.debug(f"Other grid has extra fields: {extra_fields_b}")
            return False
    return is_equal


def _check_array_equal(array_a: FancyArray, array_b: FancyArray, ignore_extras: bool) -> bool:
    # compare two FancyArrays, optionally ignoring extra columns in array_b. NaN values are treated as equal.
    columns = array_a.columns
    if ignore_extras:
        data_a = array_a[columns]
        data_b = array_b[columns]
    else:
        data_a = array_a.data
        data_b = array_b.data

    if array_equal_with_nan(data_a, data_b):
        return True
    return False
