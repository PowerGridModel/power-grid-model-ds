from power_grid_model_ds._core.model.arrays.pgm_arrays import SourceArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds.utils import fix_branch_orientations


def test_fix_branch_orientations():
    grid = Grid.from_txt("2 1", "3 2")
    source = SourceArray.empty(1)
    source.node = 1

    grid.append(source)
    updated_branches = fix_branch_orientations(grid)
    assert updated_branches.size