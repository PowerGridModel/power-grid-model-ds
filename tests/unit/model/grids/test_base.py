# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Grid tests"""

import dataclasses
from copy import deepcopy

import numpy as np
from numpy.testing import assert_equal

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


def test_repr_includes_graph_and_arrays(basic_grid: Grid):
    repr_str = repr(basic_grid)

    assert "graphs=GraphContainer(" in repr_str
    assert "active_graph(" in repr_str
    assert "complete_graph(" in repr_str

    assert "node=" in repr_str
    assert "line=" in repr_str
    assert "link=" in repr_str
    assert "transformer=" in repr_str
    assert "sym_load=" in repr_str
    assert "source=" in repr_str

    assert "generic_branch=" not in repr_str
    assert "asym_line=" not in repr_str


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

    def test_extended_grid_equality(self):
        """Extended grids get the default __eq__ from dataclasses.
        Make sure it works, since we had a bug in our original implementation where it failed for extended grids.
        """
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = deepcopy(grid1)

        assert grid1 == grid2

    def test_extended_grid_inequality(self):
        """Extended grids get the default __eq__ from dataclasses.
        Make sure it works, since we had a bug in our original implementation where it failed for extended grids.
        """
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = deepcopy(grid1)
        grid2.node.u_rated[0] += 1000.0

        assert grid1 != grid2
