# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from dataclasses import fields
from typing import TYPE_CHECKING, Type, TypeVar

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel
from power_grid_model_ds._core.utils.misc import array_equal_with_nan

if TYPE_CHECKING:
    from .base import Grid

G = TypeVar("G", bound="Grid")


logger = logging.getLogger(__name__)


def create_grid_from_extended_grid(grid_class: type[G], extended: G) -> G:
    """See Grid.from_extended()"""
    new_grid = grid_class.empty()

    # Add nodes first, so that branches can reference them
    new_grid.append(new_grid.node.__class__.from_extended(extended.node))

    for field in fields(new_grid):
        if field.name == "node":
            continue  # already added
        if isinstance(field.type, type) and issubclass(field.type, FancyArray):
            extended_array = getattr(extended, field.name)
            new_array = field.type.from_extended(extended_array)
            new_grid.append(new_array, check_max_id=False)
    return new_grid


def create_empty_grid(grid_class: Type[G], graph_model: type[BaseGraphModel] = RustworkxGraphModel) -> G:
    """See Grid.empty()"""
    empty_fields = grid_class._get_empty_fields()  # noqa # pylint: disable=protected-access
    empty_fields["graphs"] = GraphContainer.empty(graph_model=graph_model)
    return grid_class(**empty_fields)


def check_grid_is_equal(grid_a: "Grid", grid_b: "Grid", ignore_extras: bool = False, early_exit: bool = True) -> bool:
    """See Grid.is_equal()"""
    is_equal = True
    for field in fields(grid_a):
        if field.name in ["graphs"]:
            continue

        if ignore_extras and not hasattr(grid_b, field.name):
            continue

        value_a = getattr(grid_a, field.name)
        value_b = getattr(grid_b, field.name)

        if isinstance(value_a, FancyArray):
            arrays_are_equal = _check_array_equal(value_a, value_b, ignore_extras)
            if not arrays_are_equal:
                logger.debug(f"Array field '{field.name}' differs between grids.")
                is_equal = False
                if early_exit:
                    return False

        else:
            if value_a != value_b:
                logger.debug(f"Array field '{field.name}' differs between grids.")
                is_equal = False
                if early_exit:
                    return False

    if not ignore_extras:
        extra_fields_b = set({field.name for field in fields(grid_b)}) - set({field.name for field in fields(grid_a)})
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
