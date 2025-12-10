# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from dataclasses import fields, Field
from typing import TYPE_CHECKING, Any

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.utils.misc import array_equal_with_nan

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import FancyArrayContainer

logger = logging.getLogger("power_grid_model_ds.fancypy")  # public location of the container_equal function


def container_equal(
    container_a: "FancyArrayContainer",
    container_b: "FancyArrayContainer",
    ignore_extras: bool = False,
    early_exit: bool = True,
    ignore: list[str] = None,
) -> bool:
    """
    Compares two containers for equality.

    Args:
        container_a: The first container to compare.
        container_b: The second container to compare.
        ignore_extras:
            If True,
                ignores fields present in one container_a but not in container_b.
                ignores extra columns in arrays in container_b that are not present in container_a.
        early_exit: If True, returns False on the first detected difference.
        ignore: A list of field names to exclude from comparison.

    Returns:
        True if the containers are equal, False otherwise.
    """
    ignore = ignore or []
    is_equal = True

    for field in fields(container_a):
        if field.name in ignore or (ignore_extras and not hasattr(container_b, field.name)):
            continue

        if not _fields_are_equal(container_a, container_b, field, ignore_extras):
            is_equal = False
            if early_exit:
                return False

    if not ignore_extras and _check_for_extra_fields(container_a, container_b):
        return False

    return is_equal


def _fields_are_equal(
    container_a: "FancyArrayContainer", container_b: "FancyArrayContainer", field: "Field", ignore_extras: bool
) -> bool:
    """Compares a single field between two containers."""
    value_a = getattr(container_a, field.name)
    value_b = getattr(container_b, field.name)
    class_name = container_a.__class__.__name__

    if isinstance(value_a, FancyArray):
        if not _check_array_equal(value_a, value_b, ignore_extras):
            logger.debug(f"Array field '{field.name}' differs between {class_name}s.")
            return False
    elif value_a != value_b:
        logger.debug(f"Field '{field.name}' differs between {class_name}s.")
        return False

    return True


def _check_for_extra_fields(container_a: "FancyArrayContainer", container_b: "FancyArrayContainer") -> bool:
    """Checks if container_b has extra fields not present in container_a."""
    fields_a = {f.name for f in fields(container_a)}
    fields_b = {f.name for f in fields(container_b)}
    extra_fields = fields_b - fields_a

    if extra_fields:
        logger.debug(f"Container {container_b.__class__.__name__} has extra fields: {extra_fields}")
        return True
    return False


def _check_array_equal(array_a: FancyArray, array_b: FancyArray, ignore_extras: bool) -> bool:
    """
    Compares two FancyArrays, optionally ignoring extra columns in array_b.
    NaN values are treated as equal.
    """
    data_a = array_a.data
    data_b = array_b.data

    if ignore_extras:
        common_columns = [col for col in array_a.columns if col in array_b.columns]
        data_a = array_a[common_columns]
        data_b = array_b[common_columns]

    return array_equal_with_nan(data_a, data_b)