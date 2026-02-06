# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays.pgm_arrays import NodeArray
from power_grid_model_ds._core.visualizer.layout import layout_config


class CoordinatedNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


@pytest.mark.parametrize(
    "name, expected",
    [
        ("random", {"name": "random"}),
        ("circle", {"name": "circle"}),
        ("concentric", {"name": "concentric"}),
        ("grid", {"name": "grid"}),
        ("cose", {"name": "cose"}),
        ("breadthfirst", {"name": "breadthfirst", "spacingFactor": 2.5, "roots": '[id = "100"], [id = "101"]'}),
    ],
)
def test_layout_with_config(name, expected):
    result = layout_config.layout_with_config(name, source_nodes=[100, 101])
    assert result == expected


def test_get_default_graph_layout_with_xy():
    nodes = CoordinatedNodeArray.zeros(3)
    assert layout_config.get_default_graph_layout(nodes) == "preset"


def test_get_default_graph_layout():
    nodes = NodeArray.zeros(3)
    assert layout_config.get_default_graph_layout(nodes) == "breadthfirst"
