# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import SourceArray
from tests.fixtures.grid_classes import ExtendedGrid


@pytest.fixture
def grid1() -> Grid:
    """Build a basic grid to test merging"""
    return Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")


@pytest.fixture
def grid2() -> Grid:
    """Build a basic grid to merge into the first grid"""
    return Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")


class TestMergeGrids:
    def test_merge_grid(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S11 12", "S11 13 link", "13 14 transformer")

        grid1.merge(grid2, mode="keep_ids")

        assert grid1.node.id.tolist() == [1, 2, 3, 4, 11, 12, 13, 14], (
            "Merged node ids should be equal to those of grid1 and grid2 combined"
        )

    def test_merge_grid_with_some_identical_node_ids(self, grid2: Grid):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        source = SourceArray(id=[501], node=[1], status=[1], u_ref=[0.0])
        grid1.append(source)
        grid2.append(source)

        grid1.merge(grid2, mode="recalculate_ids")
        grid1.check_ids()

        # The node ids of the second grid should be offset by 501:
        assert grid1.node.id.tolist() == [1, 2, 3, 4, 502, 503, 514, 515]

        # Verify the lines, links and transformers in the resulting grid:
        columns_to_check = ["id", "from_node", "to_node"]
        assert grid1.line.data[columns_to_check].tolist() == [(5, 1, 2), (516, 502, 503)]
        assert grid1.link.data[columns_to_check].tolist() == [(6, 1, 3), (517, 502, 514)]
        assert grid1.transformer.data[columns_to_check].tolist() == [(7, 3, 4), (518, 514, 515)]

        # Verify nodes in grid.source:
        assert grid1.source.node.tolist() == [1, 502]

    def test_merge_grid_with_some_identical_lines(self, grid1: Grid, grid2: Grid):
        # Now both grids have 14 as highest node id, so both will have branch ids 15, 16 and 17:

        grid1.merge(grid2, mode="recalculate_ids")
        grid1.check_ids()

    def test_merge_grid_with_some_identical_lines_failing(self, grid1: Grid, grid2: Grid):
        with pytest.raises(ValueError):
            grid1.merge(grid2, mode="keep_ids")

    def test_merge_grid_into_a_grid_with_different_arrays(self, grid1: Grid):
        extended_grid = ExtendedGrid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        # Test that merging into a grid another grid with more arrays throws a type error
        # since we cannot append those arrays to anything:
        with pytest.raises(TypeError):
            grid1.merge(extended_grid, mode="recalculate_ids")

        # The other way around: test that merging into a grid another grid that lacks some arrays throws a type error
        # since those arrays will not be appended with anything:
        with pytest.raises(TypeError):
            extended_grid.merge(grid1, mode="recalculate_ids")  # type: ignore[arg-type]

    def test_merging_with_incorrect_mode(self, grid1: Grid, grid2: Grid):
        with pytest.raises(NotImplementedError):
            grid1.merge(grid2, mode="invalid_mode")  # type: ignore[arg-type]
