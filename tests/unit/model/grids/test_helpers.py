# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import SourceArray


class TestMergeGrids:
    def test_merge_two_grids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S11 12", "S11 13 link", "13 14 transformer")

        grid1.merge(grid2, mode="keep_ids")


        assert grid1.node.id.tolist() == [1, 2, 3, 4, 11, 12, 13, 14], "Merged node ids should be equal to those of grid1 and grid2 combined"

    def test_merge_two_grids_with_overlapping_node_ids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")
        source = SourceArray(id=[501], node=[1], status=[1], u_ref=[0.0])
        grid1.append(source)
        grid2.append(source)

        grid1.merge(grid2, mode="recalculate_ids")
        assert grid1.check_ids() is None, "Asset ids are not unique after merging!"

        # Check if from and to nodes are updated by checking that their values form the entire set of node ids:
        assert set(grid1.branches.from_node).union(grid1.branches.to_node) == set(grid1.node.id), (
            "All from and to nodes should form the entire set of node ids in the merged grid!"
        )

        # assert node in grid.source is updated by checking if the node column contains values that are all node ids:
        assert set(grid1.source.node).issubset(grid1.node.id), "All source nodes should be valid node ids!"

    def test_merge_two_grids_with_overlapping_line(self):
        # Now both grids have 14 as highest node id, so both will have branch ids 15, 16 and 17:
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        grid1.merge(grid2, mode="recalculate_ids")
        assert grid1.check_ids() is None, "Asset ids are not unique after merging!"

    def test_merge_two_grids_with_overlapping_line_failing(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        with pytest.raises(ValueError):
            grid1.merge(grid2, mode="keep_ids")
