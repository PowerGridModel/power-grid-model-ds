# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

import power_grid_model_ds.fancypy as fp
from power_grid_model_ds._core.model.arrays.pgm_arrays import LineArray, SourceArray
from power_grid_model_ds._core.model.graphs.errors import GraphError
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.utils.grid import set_branch_orientations


class TestSetBranchOrientations:
    def test_set_branch_orientations(self):
        grid = Grid.from_txt("2 1 4", "3 2 5")
        source = SourceArray.empty(1)
        source.node = 1

        grid.append(source)

        assert grid.branches.from_node.tolist() == [2, 3]
        assert grid.branches.to_node.tolist() == [1, 2]

        reversed_branches = set_branch_orientations(grid)
        assert reversed_branches == [4, 5]

        assert grid.branches.from_node.tolist() == [1, 2]
        assert grid.branches.to_node.tolist() == [2, 3]

    def test_set_branch_orientations_dry_run(self):
        grid = Grid.from_txt("2 1", "3 2")
        source = SourceArray.empty(1)
        source.node = 1
        grid.append(source)

        assert grid.branches.from_node.tolist() == [2, 3]
        assert grid.branches.to_node.tolist() == [1, 2]

        reversed_branches = set_branch_orientations(grid, dry_run=True)

        assert reversed_branches == [4, 5]
        assert grid.branches.from_node.tolist() == [2, 3]
        assert grid.branches.to_node.tolist() == [1, 2]

    @pytest.mark.parametrize(
        "txt_grid,expected_txt_grid",
        [
            (["1 2", "3 2", "3 1"], ["1 2", "2 3", "1 3"]),
            (["1 2", "2 3", "3 4", "4 1"], ["1 2", "2 3", "4 3", "1 4"]),
            (["2 1", "2 3", "1 3"], ["1 2", "3 2", "1 3"]),
            (["1 2", "2 3", "3 4", "4 2"], ["1 2", "2 3", "3 4", "2 4"]),
        ],
    )
    def test_set_branch_orientations_cycle(self, txt_grid, expected_txt_grid):
        grid = Grid.from_txt(*txt_grid)
        source = SourceArray.empty(1)
        source.node = 1
        grid.append(source)

        set_branch_orientations(grid)

        expected_grid = Grid.from_txt(*expected_txt_grid)
        assert fp.array_equal(grid.branches, expected_grid.branches)

    def test_set_branch_orientations_connected_sources(self):
        grid = Grid.from_txt("1 2", "2 3")
        source1 = SourceArray.empty(1)
        source1.node = 1
        source2 = SourceArray.empty(1)
        source2.node = 3
        grid.append(source1)
        grid.append(source2)

        with pytest.raises(GraphError, match="Cannot set branch orientations if source is connected to other sources"):
            set_branch_orientations(grid)

    @pytest.mark.parametrize(
        "txt_grid,n_reversed",
        [
            (
                ["1 2", "2 3", "2 3"],
                0,
            ),
            (
                ["2 1", "2 3", "2 3"],
                1,
            ),
            (
                ["2 1", "3 2", "2 3"],
                2,
            ),
        ],
    )
    def test_set_branch_orientations_parallel_lines(self, txt_grid: list[str], n_reversed: int):
        grid = Grid.from_txt(*txt_grid)
        source = SourceArray.empty(1)
        source.node = 1
        grid.append(source)

        reversed_branches = set_branch_orientations(grid)
        assert len(reversed_branches) == n_reversed


    def test_set_branch_orientations_open_line(self):
        grid = Grid.from_txt("1 2 11", "3 2 12")
        source = SourceArray.empty(1)
        source.node = 1
        grid.append(source)

        # Open the line from 3 to 2.
        grid.make_inactive(grid.line.get(12), at_to_side=False)
        reversed_branches = set_branch_orientations(grid)
        assert len(reversed_branches) == 1

        assert grid.branches.from_node.tolist() == [1, 2]
        assert grid.branches.to_node.tolist() == [2, 3]


    def test_set_branch_orientations_open_line_different_side(self):
        # A branch should not be reversed if the open side is already on the to side
        grid = Grid.from_txt("1 2 11", "3 2 12,open")
        source = SourceArray.empty(1)
        source["node"] = 1
        grid.append(source)

        source2 = SourceArray.empty(1)
        source2["node"] = 3
        grid.append(source2)

        # Open the line from 3 to 2.
        reversed_branches = set_branch_orientations(grid)
        assert len(reversed_branches) == 0

        assert grid.branches.from_node.tolist() == [1, 3]
        assert grid.branches.to_node.tolist() == [2, 2]
