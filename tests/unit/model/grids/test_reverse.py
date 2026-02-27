# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import numpy as np
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds import fancypy as fp
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.arrays.pgm_arrays import BranchArray, SourceArray
from power_grid_model_ds._core.model.graphs.errors import GraphError
from power_grid_model_ds._core.model.grids._reverse import get_reversed_branches, set_branch_orientations


class TestGetReversedBranches:
    def test_get_reversed_branches(self):
        grid = Grid.from_txt("2 1 4 ", "3 2 5")
        source = SourceArray.empty(1)
        source.node = 1
        grid.append(source)

        assert grid.branches.from_node.tolist() == [2, 3]
        assert grid.branches.to_node.tolist() == [1, 2]

        reversed_branches = get_reversed_branches(grid)
        assert reversed_branches.id.tolist() == [4, 5]


class TestReverseBranches:
    def test_reverse_line(self, basic_grid: Grid):
        line = basic_grid.line.get(from_node=102, to_node=103)
        basic_grid.reverse_branches(line)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=102, to_node=103)

        new_line = basic_grid.line.get(from_node=103, to_node=102)

        assert new_line.from_node == line.to_node
        assert new_line.to_node == line.from_node
        assert new_line.id == line.id

    def test_reverse_branch(self, basic_grid: Grid):
        branch = basic_grid.branches.get(from_node=101, to_node=102)
        basic_grid.reverse_branches(branch)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=101, to_node=102)

        new_branch = basic_grid.line.get(from_node=102, to_node=101)

        assert new_branch.from_node == branch.to_node
        assert new_branch.to_node == branch.from_node
        assert new_branch.id == branch.id

    def test_reverse_all_branches(self, basic_grid: Grid):
        from_nodes = basic_grid.branches.from_node
        to_nodes = basic_grid.branches.to_node

        basic_grid.reverse_branches(basic_grid.branches)

        assert np.all(from_nodes == basic_grid.branches.to_node)
        assert np.all(to_nodes == basic_grid.branches.from_node)

    def test_reverse_no_branches(self, basic_grid: Grid):
        basic_grid.reverse_branches(BranchArray())

    def test_reverse_statusses(self):
        grid = Grid.from_txt("101 102 open", "103 104")

        assert grid.branches.from_node.tolist() == [101, 103]
        assert grid.branches.from_status.tolist() == [1, 1]
        assert grid.branches.to_node.tolist() == [102, 104]
        assert grid.branches.to_status.tolist() == [0, 1]

        grid.reverse_branches(grid.branches)

        assert grid.branches.from_node.tolist() == [102, 104]
        assert grid.branches.from_status.tolist() == [0, 1]
        assert grid.branches.to_node.tolist() == [101, 103]
        assert grid.branches.to_status.tolist() == [1, 1]


class TestSetBranchOrientations:
    """Implicitly tests get_reversed_branches too."""

    def test_set_branch_orientations(self):
        grid = Grid.from_txt("2 1 4", "3 2 5")
        source = SourceArray.empty(1)
        source.node = 1

        grid.append(source)

        assert grid.branches.from_node.tolist() == [2, 3]
        assert grid.branches.to_node.tolist() == [1, 2]

        reversed_branches = set_branch_orientations(grid)
        assert reversed_branches.id.tolist() == [4, 5]

        assert grid.branches.from_node.tolist() == [1, 2]
        assert grid.branches.to_node.tolist() == [2, 3]

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
