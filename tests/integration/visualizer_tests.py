# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import sys
from pathlib import Path

# Add repo root to path so tests module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dataclasses import dataclass

import numpy as np
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.dtypes.typing import NDArray3
from power_grid_model_ds.arrays import LineArray, SourceArray
from power_grid_model_ds.generators import RadialGridGenerator
from power_grid_model_ds.visualizer import visualize
from tests.unit.visualizer.test_parsers import CoordinatedNodeArray


class ThreePhaseCoordinatedLineArray(LineArray):
    three_phase_quantity: NDArray3[np.float64]


@dataclass
class ThreePhaseCoordinatedGrid(Grid):
    node: CoordinatedNodeArray
    line: ThreePhaseCoordinatedLineArray


def get_radial_grid() -> Grid:
    grid = RadialGridGenerator(Grid).run()
    grid.set_feeder_ids()
    return grid


def get_coordinated_three_phase_grid() -> ThreePhaseCoordinatedGrid:
    scale = 500
    grid = ThreePhaseCoordinatedGrid.from_txt(
        "S1 2 open", "2 3", "3 4", "S1 500000000", "500000000 6", "6 7 transformer,open"
    )

    source = SourceArray.empty(1)
    source.node = 1
    grid.append(source)
    grid.node.x = [3, 2.5, 2, 1.5, 3.5, 4, 4.5]
    grid.node.x *= scale
    grid.node.y = [3, 4, 3, 4, 3, 4, 3]
    grid.node.y *= scale
    grid.line.three_phase_quantity = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [np.nan, np.nan, np.nan]])
    return grid


def get_grid_with_links() -> Grid:
    return Grid.from_txt("S1 2 transformer", "2 3 link", "3 4")


def visualize_grid():
    grid = get_radial_grid()
    visualize(grid=grid, debug=True)


def visualize_coordinated_three_phase_grid():
    visualize(
        grid=get_coordinated_three_phase_grid(),
        debug=True,
    )


def visualize_grid_with_links():
    visualize(grid=get_grid_with_links(), debug=True)


def visualize_grid_with_all_types():
    grid = Grid.from_txt(
        "1 2 12",
        "2 3 link,23",
        "3 4 transformer,34",
        "4 5 generic_branch,45",
        "5 6 asym_line,56",
    )
    visualize(grid=grid, debug=True)


def visualize_grid_with_all_open_types():
    grid = Grid.from_txt(
        "1 2 12,open",
        "2 3 link,23,open",
        "3 4 transformer,34,open",
        "4 5 generic_branch,45,open",
        "5 6 asym_line,56,open",
    )
    visualize(grid=grid, debug=True)


def visualize_grid_with_batch_data():
    grid = get_coordinated_three_phase_grid()
    lines_update = initialize_array(DatasetType.update, ComponentType.line, (4, 2))
    lines_update["id"] = grid.line.id[:2]
    lines_update["from_status"][:] = 1
    lines_update["from_status"][1, 0] = 0
    update_data = {ComponentType.line: lines_update}

    nodes_output = initialize_array(DatasetType.asym_output, ComponentType.node, (4, 3))
    nodes_output["id"] = grid.node.id[:3]
    nodes_output["u"] = [
        [[401.0, 402.0, 403.0], [404.0, 405.0, 406.0], [407.0, 408.0, 409.0]],
        [[410.0, 411.0, 412.0], [413.0, 414.0, 415.0], [416.0, 417.0, 418.0]],
        [[419.0, 420.0, 421.0], [422.0, 423.0, 424.0], [425.0, 426.0, 427.0]],
        [[428.0, 429.0, 430.0], [431.0, 432.0, 433.0], [434.0, 435.0, 436.0]],
    ]
    nodes_output["energized"][:] = 1
    nodes_output["energized"][1, 2] = 0
    output_data = {ComponentType.node: nodes_output}
    visualize(grid=grid, update_data=update_data, output_data=output_data, debug=True)


if __name__ == "__main__":
    # visualize_grid()
    # visualize_coordinated_three_phase_grid()
    # visualize_grid_with_links()
    # visualize_grid_with_all_types()
    # visualize_grid_with_batch_data()
    visualize_grid_with_all_open_types()
