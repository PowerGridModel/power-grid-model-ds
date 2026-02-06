# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.typing import NDArray
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays import LineArray, NodeArray
from power_grid_model_ds._core.model.arrays.pgm_arrays import Branch3Array, ThreeWindingTransformerArray
from power_grid_model_ds._core.visualizer.parsers import (
    parse_branch3_array,
    parse_branch_array,
    parse_node_array,
)
from power_grid_model_ds._core.visualizer.parsing_utils import PGM_ID_KEY
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass
from power_grid_model_ds._core.visualizer.typing import VizToComponentElements


class CoordinatedNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


def _fill_expected_with_defaults(array, expected_elements):
    for element in expected_elements:
        for col in array.columns:
            if col not in expected_elements[element]["data"]:
                expected_elements[element]["data"][col] = array[0][col].item()
    return expected_elements


@pytest.fixture
def node_array() -> tuple[NodeArray, VizToComponentElements]:
    nodes = NodeArray.zeros(4)
    nodes[:] = 99
    nodes["id"] = [1, 2, 3, 4]
    nodes["u_rated"] = [100.0, 200.0, 300.0, 400.0]

    expected_elements = {
        str(nodes["id"][i]): {
            "data": {
                "id": str(nodes["id"][i]),
                PGM_ID_KEY: nodes["id"][i].item(),
                "group": "node",
                "u_rated": nodes["u_rated"][i].item(),
            },
            "classes": f"{StyleClass.NODE.value}",
        }
        for i in range(4)
    }
    _fill_expected_with_defaults(nodes, expected_elements)

    return nodes, expected_elements


@pytest.fixture
def node_array_with_coordinates() -> tuple[CoordinatedNodeArray, VizToComponentElements]:
    nodes = CoordinatedNodeArray.zeros(4)
    nodes[:] = 99
    nodes["id"] = [1, 2, 3, 4]
    nodes["x"] = [10.0, 20.0, 30.0, 40.0]
    nodes["y"] = [10.0, 20.0, 30.0, 40.0]
    nodes["u_rated"] = [100.0, 200.0, 300.0, 400.0]

    expected_elements = {
        str(nodes["id"][i]): {
            "data": {
                "id": str(nodes["id"][i]),
                PGM_ID_KEY: nodes["id"][i].item(),
                "group": "node",
                "u_rated": nodes["u_rated"][i].item(),
                "x": nodes["x"][i].item(),
                "y": nodes["y"][i].item(),
            },
            "position": {
                "x": nodes["x"][i].item(),
                "y": -nodes["y"][i].item(),
            },
            "classes": f"{StyleClass.NODE.value}",
        }
        for i in range(4)
    }
    _fill_expected_with_defaults(nodes, expected_elements)

    return nodes, expected_elements


@pytest.fixture
def line_array() -> tuple[LineArray, VizToComponentElements]:
    lines = LineArray.zeros(3)
    lines[:] = 99
    lines["id"] = [100, 101, 102]
    lines["from_node"] = [1, 2, 3]
    lines["to_node"] = [4, 5, 6]

    expected_elements = {
        str(lines["id"][i]): {
            "data": {
                "id": str(lines["id"][i]),
                PGM_ID_KEY: lines["id"][i].item(),
                "group": "line",
                "source": str(lines["from_node"][i]),
                "target": str(lines["to_node"][i]),
                "from_node": lines["from_node"][i].item(),
                "to_node": lines["to_node"][i].item(),
            },
            "classes": f"{StyleClass.BRANCH.value}",
        }
        for i in range(3)
    }
    _fill_expected_with_defaults(lines, expected_elements)

    return lines, expected_elements


@pytest.fixture
def branch3_array() -> tuple[Branch3Array, VizToComponentElements]:
    branch3 = ThreeWindingTransformerArray.zeros(1)
    branch3[:] = 99
    branch3["id"] = [200]
    branch3["node_1"] = [1]
    branch3["node_2"] = [2]
    branch3["node_3"] = [3]
    branch3["uk_12"] = [0.1]

    expected_elements = {
        "200_0": {
            "data": {
                "id": "200_0",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "1",
                "target": "2",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_1": {
            "data": {
                "id": "200_1",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "1",
                "target": "3",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_2": {
            "data": {
                "id": "200_2",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "2",
                "target": "3",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
    }
    _fill_expected_with_defaults(branch3, expected_elements)
    return branch3, expected_elements


@pytest.mark.parametrize(
    "func, test_data, kwargs",
    [
        (parse_node_array, "node_array", {}),
        (parse_node_array, "node_array_with_coordinates", {}),
        (parse_branch_array, "line_array", {"group": ComponentType.line}),
        (parse_branch3_array, "branch3_array", {"group": ComponentType.three_winding_transformer}),
    ],
)
def test_parsing(func, request, test_data, kwargs):
    array, expected_elements = request.getfixturevalue(test_data)

    result = func(array, **kwargs)

    assert len(result) == len(expected_elements)
    assert result == expected_elements
