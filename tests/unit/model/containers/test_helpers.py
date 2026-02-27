# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.containers.helpers import container_equal
from tests.fixtures.grid_classes import ExtendedGrid
from tests.fixtures.grids import build_basic_grid


class TestContainerEqual:
    def test_grids_equal(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        assert container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_different_nodes(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        # modify a node
        grid2.node.u_rated[0] += 1000.0
        assert not container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_different_type(self):
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = Grid.from_extended(grid1)
        assert not container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_ignore_extras(self, basic_grid: Grid):
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = Grid.from_extended(grid1)
        assert container_equal(grid1, grid2, ignore_extras=True, fields_to_ignore=["graphs"])
        assert container_equal(grid1, grid2, ignore_extras=True)
        assert not container_equal(grid1, grid2, ignore_extras=False, fields_to_ignore=["graphs"])
