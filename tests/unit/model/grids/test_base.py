# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Grid tests"""

import dataclasses
from copy import deepcopy

import numpy as np
from numpy.testing import assert_equal

from power_grid_model_ds._core.model.arrays import SourceArray
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.grid_classes import ExtendedGrid
from tests.fixtures.grids import build_basic_grid

# pylint: disable=missing-function-docstring,missing-class-docstring


def test_initialize_empty_grid(grid: Grid):
    assert isinstance(grid, Grid)
    fields = dataclasses.asdict(grid).keys()
    assert {
        "_id_counter",
        "asym_current_sensor",
        "asym_line",
        "asym_power_sensor",
        "asym_voltage_sensor",
        "generic_branch",
        "graphs",
        "line",
        "link",
        "node",
        "source",
        "sym_current_sensor",
        "sym_gen",
        "sym_load",
        "sym_power_sensor",
        "sym_voltage_sensor",
        "three_winding_transformer",
        "transformer",
        "transformer_tap_regulator",
    } == set(fields)


def test_initialize_empty_extended_grid():
    grid = ExtendedGrid.empty()
    assert isinstance(grid, ExtendedGrid)


def test_from_extended_grid():
    extended_grid = build_basic_grid(ExtendedGrid.empty())
    grid = Grid.from_extended(extended_grid)
    assert not isinstance(grid, ExtendedGrid)
    assert_equal(grid.line.data, extended_grid.line.data[grid.line.columns])
    assert grid.node.size
    assert grid.branches.size
    assert grid.graphs.active_graph.nr_nodes == len(grid.node)
    assert grid.graphs.complete_graph.nr_nodes == len(grid.branches)

    assert extended_grid.id_counter == grid.id_counter
    assert extended_grid.max_id == grid.max_id


def test_basic_grid_fixture(basic_grid: Grid):
    grid = basic_grid

    # The grid consists of 6 nodes
    assert 6 == len(grid.node)
    # 1 of these is a source
    assert 1 == len(grid.source)
    # 4 of these have a load attaches
    assert 4 == len(grid.sym_load)

    inactive_mask = np.logical_or(grid.line.from_status == 0, grid.line.to_status == 0)
    inactive_lines = grid.line[inactive_mask]
    # we have placed 1 normally open point
    assert 1 == len(inactive_lines)

    # All nodes should be in both graphs
    assert len(grid.graphs.active_graph.external_ids) == len(grid.node)
    assert len(grid.graphs.complete_graph.external_ids) == len(grid.node)

    nr_branches = len(grid.line) + len(grid.transformer) + len(grid.link)
    assert nr_branches == grid.graphs.complete_graph.nr_branches
    assert nr_branches - 1 == grid.graphs.active_graph.nr_branches

    inactive_mask = np.logical_or(grid.line.from_status == 0, grid.line.to_status == 0)
    inactive_lines = grid.line[inactive_mask]
    # we have placed 1 normally open point
    assert 1 == len(inactive_lines)

    assert len(grid.line) + len(grid.transformer) + len(grid.link) - 1 == grid.graphs.active_graph.nr_branches
    assert len(grid.line) + len(grid.transformer) + len(grid.link) == grid.graphs.complete_graph.nr_branches


class TestGridEquality:
    def test_grids_equal(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        assert grid1 == grid2

    def test_different_nodes(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        # modify a node
        grid2.node.u_rated[0] += 1000.0
        assert grid1 != grid2

    def test_different_lines(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = build_basic_grid(Grid.empty())
        # modify a line
        grid2.line.r1[0] += 0.01
        assert grid1 != grid2

    def test_different_type(self):
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = Grid.from_extended(grid1)

        assert grid1 != grid2


class TestMergeGrids:
    def test_merge_two_grids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S11 12", "S11 13 link", "13 14 transformer")
        grid1_size = grid1.node.size
        grid2_size = grid2.node.size

        merged_grid = grid1.merge(grid2, mode="keep_ids")
        merged_grid_size = merged_grid.node.size

        assert merged_grid_size == grid1_size + grid2_size, "Merged grid size should be the sum of both grids' sizes"

    def test_merge_two_grids_with_overlapping_node_ids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")
        source = SourceArray(id=[501], node=[1], status=[1], u_ref=[0.0])
        grid1.append(source)
        grid2.append(source)

        merged_grid = grid1.merge(grid2, mode="recalculate_ids")
        assert merged_grid.check_ids() is None, "Asset ids are not unique after merging!"

        # Check if from and to nodes are updated by checking that their values form the entire set of node ids:
        assert set(merged_grid.branches.from_node).union(merged_grid.branches.to_node) == set(merged_grid.node.id), (
            "All from and to nodes should form the entire set of node ids in the merged grid!"
        )

        # assert node in grid.source is updated by checking if the node column contains values that are all node ids:
        assert set(merged_grid.source.node).issubset(merged_grid.node.id), "All source nodes should be valid node ids!"

    def test_merge_two_grids_with_overlapping_line(self):
        # Now both grids have 14 as highest node id, so both will have branch ids 15, 16 and 17:
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        merged_grid = grid1.merge(grid2, mode="recalculate_ids")
        assert merged_grid.check_ids() is None, "Asset ids are not unique after merging!"
