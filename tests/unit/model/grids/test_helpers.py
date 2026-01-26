# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import SourceArray
from tests.fixtures.grid_classes import ExtendedGrid


class TestMergeGrids:
    def test_merge_grid(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S11 12", "S11 13 link", "13 14 transformer")

        grid1.merge(grid2, mode="keep_ids")

        assert grid1.node.id.tolist() == [1, 2, 3, 4, 11, 12, 13, 14], (
            "Merged node ids should be equal to those of grid1 and grid2 combined"
        )

    def test_merge_grid_with_some_identical_node_ids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")
        source = SourceArray(id=[501], node=[1], status=[1], u_ref=[0.0])
        grid1.append(source)
        grid2.append(source)

        grid1.merge(grid2, mode="recalculate_ids")
        assert grid1.check_ids() is None, "Asset ids are not unique after merging!"

        expected_offset = 501
        assert grid1.node.id.tolist() == [1, 2, 3, 4] + [i + expected_offset for i in [1, 2, 13, 14]]

        # Verify the set of branches in the resulting grid:
        expected_branches = {(int(i), int(j)) for i, j in zip(grid1.branches.from_node, grid1.branches.to_node)}
        assert expected_branches == {(1, 2), (1, 3), (3, 4), (502, 503), (502, 514), (514, 515)}

        # Verify nodes in grid.source:
        assert grid1.source.node.tolist() == [1, 502]

    def test_merge_grid_with_some_identical_lines(self):
        # Now both grids have 14 as highest node id, so both will have branch ids 15, 16 and 17:
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        grid1.merge(grid2, mode="recalculate_ids")
        assert grid1.check_ids() is None, "Asset ids are not unique after merging!"

    def test_merge_grid_with_some_identical_lines_failing(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        with pytest.raises(ValueError):
            grid1.merge(grid2, mode="keep_ids")

    def test_merge_grids_with_unidentical_arrays(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = ExtendedGrid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        # Test that merging into a grid another grid with more arrays throws a type error
        # since we cannot append those arrays to anything:
        with pytest.raises(TypeError):
            grid1.merge(grid2, mode="recalculate_ids")

        # The other way around: test that merging into a grid another grid that lacks some arrays throws a type error
        # since those arrays won't be appended with anything:
        with pytest.raises(TypeError):
            grid2.merge(grid1, mode="recalculate_ids")
