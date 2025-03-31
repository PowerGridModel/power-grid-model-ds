# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

from power_grid_model_ds import Grid
from power_grid_model_ds._core.visualizer.app import visualize
from power_grid_model_ds.generators import RadialGridGenerator
from tests.unit.visualizer.test_parsers import CoordinatedNodeArray


@dataclass
class CoordinatedGrid(Grid):
    node: CoordinatedNodeArray


def get_radial_grid() -> Grid:
    return RadialGridGenerator(Grid).run()


def get_coordinated_grid() -> CoordinatedGrid:
    scale = 500
    grid = CoordinatedGrid.from_txt("S1 2 open", "2 3", "3 4", "S1 500000000", "500000000 6", "6 7 transformer")
    grid.node.x = [3, 2.5, 2, 1.5, 3.5, 4, 4.5]
    grid.node.x *= scale
    grid.node.y = [3, 4, 3, 4, 3, 4, 3]
    grid.node.y *= scale
    return grid


def visualize_grid():
    visualize(grid=get_radial_grid(), debug=True)


def visualize_coordinated_grid():
    visualize(
        grid=get_coordinated_grid(),
        debug=True,
    )


if __name__ == "__main__":
    visualize_grid()
    # visualize_coordinated_grid()
