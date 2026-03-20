# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.typing import NDArray

from power_grid_model_ds._core.visualizer.layout import layout_config
from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions
from power_grid_model_ds.arrays import NodeArray


class CoordinatedNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


@pytest.mark.parametrize(
    "name, expected",
    [
        (LayoutOptions.RANDOM, {"name": "random"}),
        (LayoutOptions.CIRCLE, {"name": "circle"}),
        (LayoutOptions.CONCENTRIC, {"name": "concentric"}),
        (LayoutOptions.GRID, {"name": "grid"}),
        (LayoutOptions.COSE, {"name": "cose"}),
        (
            LayoutOptions.BREADTHFIRST,
            {"name": "breadthfirst", "spacingFactor": 2.5, "roots": 'node[group = "source_ghost_node"]'},
        ),
    ],
)
def test_layout_with_config(name, expected):
    result = layout_config.layout_with_config(name, source_available=True)
    assert result == expected


def test_get_default_graph_layout_with_xy():
    nodes = CoordinatedNodeArray.zeros(3)
    assert layout_config.get_default_graph_layout(nodes) == LayoutOptions.PRESET


def test_get_default_graph_layout():
    nodes = NodeArray.zeros(3)
    assert layout_config.get_default_graph_layout(nodes) == LayoutOptions.BREADTHFIRST
