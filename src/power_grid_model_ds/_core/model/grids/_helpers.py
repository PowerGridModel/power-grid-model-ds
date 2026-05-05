# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import copy
import logging
from dataclasses import fields
from typing import TYPE_CHECKING, Literal, overload

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel
from power_grid_model_ds.arrays import (
    AsymCurrentSensorArray,
    AsymGenArray,
    AsymLoadArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    FaultArray,
    IdArray,
    NodeArray,
    ShuntArray,
    SourceArray,
    SymCurrentSensorArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    TransformerTapRegulatorArray,
    VoltageRegulatorArray,
)

if TYPE_CHECKING:
    from .base import Grid


_logger = logging.getLogger(__name__)


def create_grid_from_extended_grid[G: Grid](grid_class: type[G], extended: G) -> G:
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


def create_empty_grid[G: Grid](grid_class: type[G], graph_model: type[BaseGraphModel] = RustworkxGraphModel) -> G:
    """See Grid.empty()"""
    empty_fields = grid_class._get_empty_fields()  # noqa # pylint: disable=protected-access
    empty_fields["graphs"] = GraphContainer.empty(graph_model=graph_model)
    return grid_class(**empty_fields)


@overload
def merge_grids[G: Grid](grid: G, other_grid: G, mode: Literal["recalculate_ids"]) -> int: ...


@overload
def merge_grids[G: Grid](grid: G, other_grid: G, mode: Literal["keep_ids"]) -> None: ...


def merge_grids(grid, other_grid, mode: Literal["keep_ids", "recalculate_ids"]):
    """See Grid.merge()"""

    if type(grid) is not type(other_grid):
        raise TypeError("Both grids should be of the same class (to ensure they have the same arrays)")

    other_grid_all_arrays = list(other_grid.all_arrays())

    match mode:
        case "recalculate_ids":
            other_grid_all_arrays = copy.deepcopy(other_grid_all_arrays)
            offset = grid.max_id
            _increment_grid_ids_by_offset(other_grid_all_arrays, offset)
        case "keep_ids":
            offset = None
        case _:
            raise NotImplementedError(f"Merge mode {mode} is not implemented")

    # Append all arrays from the other grid to this grid
    for array in other_grid_all_arrays:
        grid.append(array, check_max_id=False)

    if mode == "keep_ids":
        try:
            grid.check_ids()
        except ValueError as e:
            raise ValueError("Asset ids are not unique after merging! Use mode='recalculate_ids' to avoid this.") from e

    return offset


def _increment_grid_ids_by_offset(all_arrays: list[FancyArray], offset: int) -> None:
    for array in all_arrays:
        for column in array.get_id_columns():
            _update_id_column(array, column, offset)


def _update_id_column(array: FancyArray, column: str, offset: int) -> None:
    mask = array.is_empty(column)
    array[column][~mask] += offset
