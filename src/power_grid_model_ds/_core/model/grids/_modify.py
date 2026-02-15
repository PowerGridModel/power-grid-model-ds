# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import logging
import warnings
from typing import TYPE_CHECKING

import numpy as np

from power_grid_model_ds._core.model.arrays import (
    AsymLineArray,
    Branch3Array,
    BranchArray,
    GenericBranchArray,
    LineArray,
    LinkArray,
    NodeArray,
    TransformerArray,
)

from ..arrays.base.array import FancyArray

if TYPE_CHECKING:
    from .base import Grid


logger = logging.getLogger(__name__)


def add_array_to_grid(grid: "Grid", array: FancyArray, check_max_id: bool = True) -> None:
    """See Grid.append()"""
    grid._append(array, check_max_id=check_max_id)  # noqa # pylint: disable=protected-access
    # pylint: disable=protected-access
    grid.graphs._append(array)


def add_node(grid: "Grid", node: NodeArray) -> None:
    """See Grid.add_node()"""
    warnings.warn(
        "Grid.add_node is deprecated and will be removed in a future release. Use Grid.append instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    grid._append(array=node)  # noqa # pylint: disable=protected-access
    grid.graphs.add_node_array(node_array=node)
    logging.debug(f"added node {node.id}")


def add_branch(grid: "Grid", branch: BranchArray) -> None:
    """See Grid.add_branch()"""
    warnings.warn(
        "Grid.add_branch is deprecated and will be removed in a future release. Use Grid.append instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    grid._append(array=branch)  # noqa # pylint: disable=protected-access
    grid.graphs.add_branch_array(branch_array=branch)

    logging.debug(f"added branch {branch.id} from {branch.from_node} to {branch.to_node}")


def reverse_branches(grid: "Grid", branches: BranchArray) -> None:
    """See Grid.reverse_branches()"""
    if not branches.size:
        return
    if not isinstance(branches, (LineArray, LinkArray, TransformerArray, GenericBranchArray, AsymLineArray)):
        try:
            branches = grid.get_typed_branches(branches.id)
        except ValueError:
            # If the branches are not of the same type, reverse them per type (though this is slower)
            for array in grid.branch_arrays:
                grid.reverse_branches(array.filter(branches.id))
            return

    from_nodes = branches.from_node
    to_nodes = branches.to_node

    array_field = grid.find_array_field(branches.__class__)
    array = getattr(grid, array_field.name)
    array.update_by_id(branches.id, from_node=to_nodes, to_node=from_nodes)


def make_active(grid: "Grid", branch: BranchArray) -> None:
    """See Grid.make_active()"""
    array_field = grid.find_array_field(branch.__class__)
    array_attr = getattr(grid, array_field.name)
    branch_mask = array_attr.id == branch.id
    array_attr.from_status[branch_mask] = 1
    array_attr.to_status[branch_mask] = 1
    setattr(grid, array_field.name, array_attr)

    grid.graphs.make_active(branch=branch)
    logging.debug(f"activated branch {branch.id}")


def make_inactive(grid, branch: BranchArray, at_to_side: bool = True) -> None:
    """See Grid.make_inactive()"""
    array_field = grid.find_array_field(branch.__class__)
    array_attr = getattr(grid, array_field.name)
    branch_mask = array_attr.id == branch.id
    status_side = "to_status" if at_to_side else "from_status"
    array_attr[status_side][branch_mask] = 0
    setattr(grid, array_field.name, array_attr)

    grid.graphs.make_inactive(branch=branch)
    logging.debug(f"deactivated branch {branch.id}")


def delete_node(grid: "Grid", node: NodeArray) -> None:
    """See Grid.delete_node()"""
    grid.node = grid.node.exclude(id=node.id)

    ids_to_exclude = np.concatenate(
        [
            grid.sym_load.filter(node=node.id).id,
            grid.asym_load.filter(node=node.id).id,
            grid.source.filter(node=node.id).id,
            grid.asym_gen.filter(node=node.id).id,
            grid.shunt.filter(node=node.id).id,
            node.id,
        ]
    )
    grid.sym_power_sensor = grid.sym_power_sensor.exclude(measured_object=ids_to_exclude)
    grid.asym_power_sensor = grid.asym_power_sensor.exclude(measured_object=ids_to_exclude)
    grid.voltage_regulator = grid.voltage_regulator.exclude(regulated_object=ids_to_exclude)

    grid.sym_voltage_sensor = grid.sym_voltage_sensor.exclude(measured_object=node.id)
    grid.asym_voltage_sensor = grid.asym_voltage_sensor.exclude(measured_object=node.id)

    grid.sym_load = grid.sym_load.exclude(node=node.id)
    grid.source = grid.source.exclude(node=node.id)
    grid.asym_load = grid.asym_load.exclude(node=node.id)
    grid.asym_gen = grid.asym_gen.exclude(node=node.id)
    grid.shunt = grid.shunt.exclude(node=node.id)

    grid.fault = grid.fault.exclude(fault_object=node.id)

    for branch_array in grid.branch_arrays:
        matching_branches = branch_array.filter(from_node=node.id, to_node=node.id, mode_="OR")
        for branch in matching_branches:
            grid.delete_branch(branch)

    matching_three_winding_transformers = grid.three_winding_transformer.filter(
        node_1=node.id, node_2=node.id, node_3=node.id, mode_="OR"
    )
    for three_winding_transformer in matching_three_winding_transformers:
        grid.delete_branch3(three_winding_transformer)

    grid.graphs.delete_node(node=node)
    logging.debug(f"deleted rail {node.id}")


def delete_branch(grid: "Grid", branch: BranchArray) -> None:
    """See Grid.delete_branch()"""
    _delete_branch_array(branch=branch, grid=grid)
    grid.graphs.delete_branch(branch=branch)
    logging.debug(f"""deleted branch {branch.id.item()} from {branch.from_node.item()} to {branch.to_node.item()}""")


def delete_branch3(grid: "Grid", branch: Branch3Array) -> None:
    """See Grid.delete_branch3()"""
    _delete_branch_array(branch=branch, grid=grid)
    grid.graphs.delete_branch3(branch=branch)
    logging.debug(f"deleted branch3 {branch.id}")


def _delete_branch_array(branch: BranchArray | Branch3Array, grid: "Grid"):
    # Delete a branch or branch3 array from the grid.
    array_field = grid.find_array_field(branch.__class__)
    array_attr = getattr(grid, array_field.name)
    setattr(grid, array_field.name, array_attr.exclude(id=branch.id))

    grid.sym_power_sensor = grid.sym_power_sensor.exclude(measured_object=branch.id)
    grid.asym_power_sensor = grid.asym_power_sensor.exclude(measured_object=branch.id)
    grid.sym_current_sensor = grid.sym_current_sensor.exclude(measured_object=branch.id)
    grid.asym_current_sensor = grid.asym_current_sensor.exclude(measured_object=branch.id)
    grid.transformer_tap_regulator = grid.transformer_tap_regulator.exclude(regulated_object=branch.id)


def delete_appliance(grid: "Grid", appliance) -> None:
    """See Grid.delete_appliance()"""
    # Delete a branch or branch3 array from the grid.
    array_field = grid.find_array_field(appliance.__class__)
    array_attr = getattr(grid, array_field.name)
    setattr(grid, array_field.name, array_attr.exclude(id=appliance.id))

    grid.sym_power_sensor = grid.sym_power_sensor.exclude(measured_object=appliance.id)
    grid.asym_power_sensor = grid.asym_power_sensor.exclude(measured_object=appliance.id)
    grid.voltage_regulator = grid.voltage_regulator.exclude(regulated_object=appliance.id)
    logging.debug(f"deleted appliance {appliance.id}")
