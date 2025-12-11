# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from numpy.testing import assert_array_equal

from power_grid_model_ds._core.model.arrays.pgm_arrays import LineArray, NodeArray
from power_grid_model_ds._core.model.constants import EMPTY_ID
from power_grid_model_ds._core.model.enums.nodes import NodeType
from tests.fixtures.grids import build_basic_grid


def test_set_feeder_ids(grid):
    """Test the setting of extra properties is_feeder and feeder_id."""
    grid = build_basic_grid(grid=grid)

    # Set all feeder ids to a value to check they have been reset
    grid.branches.feeder_branch_id = 1
    grid.node.feeder_branch_id = 1
    grid.branches.feeder_node_id = 1
    grid.node.feeder_node_id = 1

    grid.set_feeder_ids()

    assert_array_equal(grid.branches.is_feeder, np.array([False, True, False, False, True, False]))
    assert_array_equal(grid.branches.feeder_branch_id, np.array([201, 201, 201, EMPTY_ID, 204, 204]))
    assert_array_equal(grid.node.feeder_branch_id, np.array([EMPTY_ID, 201, 201, 204, 204, 201]))
    assert_array_equal(grid.branches.feeder_node_id, np.array([101, 101, 101, EMPTY_ID, 101, 101]))
    assert_array_equal(grid.node.feeder_node_id, np.array([EMPTY_ID, 101, 101, 101, 101, 101]))


def test_set_feeder_ids_unconnected_node(grid):
    """Test handling of unconnected nodes, these are set to EMPTY_ID"""
    grid = build_basic_grid(grid=grid)
    extra_node = NodeArray.empty(1)
    grid.append(extra_node)
    grid.set_feeder_ids()

    assert_array_equal(grid.branches.is_feeder, np.array([False, True, False, False, True, False]))
    assert_array_equal(grid.branches.feeder_branch_id, np.array([201, 201, 201, EMPTY_ID, 204, 204]))
    assert_array_equal(grid.node.feeder_branch_id, np.array([EMPTY_ID, 201, 201, 204, 204, 201, EMPTY_ID]))
    assert_array_equal(grid.branches.feeder_node_id, np.array([101, 101, 101, EMPTY_ID, 101, 101]))
    assert_array_equal(grid.node.feeder_node_id, np.array([EMPTY_ID, 101, 101, 101, 101, 101, EMPTY_ID]))


def test_set_feeder_ids_parallel_line(grid):
    """Test handling of parallel lines, these get the same feeder id"""
    grid = build_basic_grid(grid=grid)

    # Add a second (parallel) line from 101 to 102
    extra_line = LineArray.empty(1)
    extra_line.from_node = 101
    extra_line.to_node = 102
    extra_line.from_status = 1
    extra_line.to_status = 1
    grid.append(extra_line)

    grid.set_feeder_ids()

    assert_array_equal(grid.branches.is_feeder, np.array([False, True, False, False, True, True, False]))
    assert_array_equal(grid.branches.feeder_branch_id, np.array([201, 201, 201, EMPTY_ID, 204, 201, 204]))
    assert_array_equal(grid.node.feeder_branch_id, np.array([EMPTY_ID, 201, 201, 204, 204, 201]))
    assert_array_equal(grid.branches.feeder_node_id, np.array([101, 101, 101, EMPTY_ID, 101, 101, 101]))
    assert_array_equal(grid.node.feeder_node_id, np.array([EMPTY_ID, 101, 101, 101, 101, 101]))


def test_set_feeder_ids_inactive(grid):
    grid = build_basic_grid(grid=grid)

    # Make a feeding line inactive
    grid.make_inactive(grid.line.get(204))
    grid.make_active(grid.line.get(203))

    grid.set_feeder_ids()

    assert_array_equal(grid.branches.is_feeder, np.array([False, True, False, False, True, False]))
    assert_array_equal(grid.branches.feeder_branch_id, np.array([201, 201, 201, 201, EMPTY_ID, 201]))
    assert_array_equal(grid.node.feeder_branch_id, np.array([EMPTY_ID, 201, 201, 201, 201, 201]))
    assert_array_equal(grid.branches.feeder_node_id, np.array([101, 101, 101, 101, EMPTY_ID, 101]))
    assert_array_equal(grid.node.feeder_node_id, np.array([EMPTY_ID, 101, 101, 101, 101, 101]))


def test_set_feeder_to_node(grid):
    """Test that the feeder ids are set correctly when the branch is facing the other way"""
    # Add Substations
    substation = NodeArray(id=[100, 101], u_rated=[21_000, 10_500], node_type=[NodeType.SUBSTATION_NODE.value] * 2)
    grid.append(substation, check_max_id=False)

    # Add Nodes
    nodes = NodeArray(
        id=[102],
        u_rated=[10_500.0],
    )
    grid.append(nodes, check_max_id=False)

    # Add Lines
    lines = LineArray.empty(2)
    lines.id = [200, 201]
    lines.from_status = [1] * 2
    lines.to_status = [1] * 2
    lines.from_node = [100, 102]
    lines.to_node = [101, 101]
    grid.append(lines, check_max_id=False)

    grid.set_feeder_ids()

    assert_array_equal(grid.branches.is_feeder, np.array([False, True]))
    assert_array_equal(grid.branches.feeder_branch_id, np.array([EMPTY_ID, 201]))
    assert_array_equal(grid.node.feeder_branch_id, np.array([EMPTY_ID, EMPTY_ID, 201]))
    assert_array_equal(grid.branches.feeder_node_id, np.array([EMPTY_ID, 101]))
    assert_array_equal(grid.node.feeder_node_id, np.array([EMPTY_ID, EMPTY_ID, 101]))
