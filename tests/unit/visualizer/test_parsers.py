# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays import LineArray, NodeArray
from power_grid_model_ds._core.model.arrays.pgm_arrays import Branch3Array
from power_grid_model_ds._core.visualizer.parsers import parse_branch3_array, parse_branch_array, parse_node_array


class CoordinatedNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


class TestParseNodeArray:
    def test_parse_node_array(self):
        nodes = NodeArray.zeros(3)
        nodes["id"] = [1, 2, 3]
        nodes["u_rated"] = [10, 20.4, 30.99]

        parsed = parse_node_array(nodes)
        assert len(parsed) == 3

        node_1_data = parsed[0]["data"]
        node_2_data = parsed[1]["data"]
        node_3_data = parsed[2]["data"]

        assert node_1_data["group"] == "node"
        assert parsed[0].get("position") is None  # no coordinates

        assert node_1_data["id"] == "1"  # ids are converted to strings
        assert node_2_data["id"] == "2"
        assert node_3_data["id"] == "3"

        assert node_1_data["u_rated"] == 10
        assert node_2_data["u_rated"] == 20.4
        assert node_3_data["u_rated"] == 30.99

    def test_parse_coordinated_node_array(self):
        nodes = CoordinatedNodeArray.zeros(3)
        nodes["id"] = [1, 2, 3]
        nodes["x"] = [10, 20, 30]
        nodes["y"] = [99, 88, 77]

        parsed = parse_node_array(nodes)
        position = parsed[0].get("position")
        assert position is not None
        assert position["x"] == 10
        assert position["y"] == -99  # coordinates are inverted on y-axis


class TestParseBranches:
    def test_parse_line_array(self):
        lines = LineArray.zeros(3)
        lines["id"] = [100, 101, 102]
        lines["from_node"] = [1, 2, 3]
        lines["to_node"] = [4, 5, 6]
        parsed = parse_branch_array(lines, "line")

        assert len(parsed) == 3
        assert parsed[0]["data"]["id"] == "100"
        assert parsed[0]["data"]["source"] == "1"
        assert parsed[0]["data"]["target"] == "4"
        assert parsed[0]["data"]["group"] == "line"

    def test_parse_branch3_array(self):
        branch3 = Branch3Array.zeros(1)
        branch3["id"] = [200]
        branch3["node_1"] = [1]
        branch3["node_2"] = [2]
        branch3["node_3"] = [3]
        branch3["status_1"] = [1]
        branch3["status_2"] = [1]
        branch3["status_3"] = [1]

        parsed = parse_branch3_array(branch3, "transformer")
        assert len(parsed) == 3
        assert parsed[0]["data"]["id"] == "200_1_2"
        assert parsed[0]["data"]["source"] == "1"
        assert parsed[0]["data"]["target"] == "2"
        assert parsed[0]["data"]["group"] == "transformer"
        assert parsed[1]["data"]["id"] == "200_1_3"
        assert parsed[1]["data"]["source"] == "1"
        assert parsed[1]["data"]["target"] == "3"
        assert parsed[1]["data"]["group"] == "transformer"
        assert parsed[2]["data"]["id"] == "200_2_3"
        assert parsed[2]["data"]["source"] == "2"
        assert parsed[2]["data"]["target"] == "3"
        assert parsed[2]["data"]["group"] == "transformer"
