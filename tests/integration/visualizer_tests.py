from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds import Grid, visualize
from power_grid_model_ds.arrays import NodeArray
from power_grid_model_ds.generators import RadialGridGenerator


class TopoNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


@dataclass
class TopoGrid(Grid):
    node: TopoNodeArray


def get_radial_grid() -> Grid:
    return RadialGridGenerator(Grid).run()


def get_topo_grid() -> TopoGrid:
    scale = 500
    grid = TopoGrid.from_txt("S1 2 open", "2 3", "3 4", "S1 500000000", "500000000 6", "6 7 transformer")
    grid.node.x = [3, 2.5, 2, 1.5, 3.5, 4, 4.5]
    grid.node.x *= scale
    grid.node.y = [3, 4, 3, 4, 3, 4, 3]
    grid.node.y *= scale
    return grid


def visualize_grid():
    visualize(grid=get_radial_grid(), debug=True)


def visualize_topo_grid():
    visualize(grid=get_topo_grid(), debug=True, )


if __name__ == "__main__":
    visualize_grid()
    # visualize_topo_grid()
