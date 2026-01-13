# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import logging
from typing import TYPE_CHECKING, Type, TypeVar

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.graphs.container import GraphContainer

from ..graphs.models import RustworkxGraphModel
from ..graphs.models.base import BaseGraphModel

if TYPE_CHECKING:
    from .base import Grid

from power_grid_model_ds._core.model.arrays import (
    NodeArray,
    SourceArray,
    SymLoadArray, SymPowerSensorArray, SymVoltageSensorArray, AsymVoltageSensorArray, TransformerTapRegulatorArray,
    BranchArray, Branch3Array, SymGenArray, IdArray,
)

G = TypeVar("G", bound="Grid")


logger = logging.getLogger(__name__)


def create_grid_from_extended_grid(grid_class: type[G], extended: G) -> G:
    """See Grid.from_extended()"""
    new_grid = grid_class.empty()

    # Add nodes first, so that branches can reference them
    new_grid.append(new_grid.node.__class__.from_extended(extended.node))

    for field in dataclasses.fields(new_grid):
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


import copy

def merge_grids(grid: G, other_grid: G) -> G:
    """See Grid.merge()"""
    new_grid = copy.deepcopy(grid)
    other_grid_reindexed = copy.deepcopy(other_grid)

    # Todo: turn into recalculate_ids() function
    # First offset the ids of other_grid to avoid conflicts
    ids_grid = grid.node.id
    ids_other_grid = other_grid.node.id
    overlapping_ids = set(ids_grid).intersection(set(ids_other_grid))
    if overlapping_ids:  # If any index overlaps, then bump columns with references to node ids
        offset = grid.id_counter  # Todo: grid.id_counter - other_grid.min_id() + 1
        _increment_grid_ids_by_offset(other_grid_reindexed, offset=offset)

    # Now append all arrays from other_grid to grid
    for array in other_grid_reindexed.all_arrays():
        new_grid.append(array, check_max_id=False)

    return new_grid


def _increment_grid_ids_by_offset(grid: G, offset: int) -> None:
    for array in grid.all_arrays():
        # print(array)
        if isinstance(array, IdArray):
            array.id += offset
        if isinstance(array, NodeArray | SymPowerSensorArray | SymVoltageSensorArray | AsymVoltageSensorArray):
            continue
        elif isinstance(array, TransformerTapRegulatorArray):
            array.regulated_object += offset
        elif isinstance(array, BranchArray):
            array.from_node += offset
            array.to_node += offset
        elif isinstance(array, Branch3Array):
            array.node_1 += offset
            array.node_2 += offset
            array.node_3 += offset
        elif isinstance(array, SymGenArray | SymLoadArray | SourceArray):
            array.node += offset
        else:
            raise NotImplementedError(f"The array of type {type(array)} is not implemented for appending")
        # print()