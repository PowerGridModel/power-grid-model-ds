# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for coincident-node display positioning."""

from copy import deepcopy

from power_grid_model_ds._core.visualizer.layout.node_overlap import (
    separate_coincident_nodes,
)


def make_node(node_id, x, y):
    return {
        "data": {"id": node_id, "group": "node"},
        "position": {"x": x, "y": y},
        "classes": "node",
    }


def make_line(line_id, source, target):
    return {
        "data": {
            "id": line_id,
            "group": "line",
            "source": source,
            "target": target,
        },
        "classes": "branch",
    }


def test_separates_two_coincident_nodes():
    elements = {
        "2": make_node("2", 250.0, -250.0),
        "3": make_node("3", 250.0, -250.0),
    }

    result = separate_coincident_nodes(elements)

    assert result["2"]["position"] != result["3"]["position"]
    assert result["2"]["position"]["y"] == -250.0
    assert result["3"]["position"]["y"] == -250.0


def test_preserves_non_overlapping_nodes():
    elements = {
        "1": make_node("1", 0.0, 0.0),
        "2": make_node("2", 500.0, 500.0),
    }

    assert separate_coincident_nodes(elements) == elements


def test_preserves_connectivity_and_input():
    elements = {
        "1": make_node("1", 0.0, -250.0),
        "2": make_node("2", 250.0, -250.0),
        "3": make_node("3", 250.0, -250.0),
        "4": make_node("4", 500.0, -250.0),
        "5": make_line("5", "1", "2"),
        "6": make_line("6", "3", "4"),
    }

    original = deepcopy(elements)
    result = separate_coincident_nodes(elements)

    assert elements == original
    assert result["5"] == original["5"]
    assert result["6"] == original["6"]

    assert result["2"]["position"] != result["3"]["position"]

    assert result["5"]["data"]["source"] == "1"
    assert result["5"]["data"]["target"] == "2"
    assert result["6"]["data"]["source"] == "3"
    assert result["6"]["data"]["target"] == "4"


def test_separates_three_coincident_nodes():
    elements = {str(node_id): make_node(str(node_id), 250.0, -250.0) for node_id in (1, 2, 3)}

    result = separate_coincident_nodes(elements)

    positions = {(element["position"]["x"], element["position"]["y"]) for element in result.values()}

    assert len(positions) == 3


def test_ignores_nodes_without_coordinates():
    elements = {
        "1": {"data": {"id": "1", "group": "node"}, "classes": "node"},
        "2": {"data": {"id": "2", "group": "node"}, "classes": "node"},
    }

    assert separate_coincident_nodes(elements) == elements


def test_deterministic_positions():
    elements = {
        "3": make_node("3", 250.0, -250.0),
        "2": make_node("2", 250.0, -250.0),
    }

    assert separate_coincident_nodes(elements) == separate_coincident_nodes(elements)


def test_separation_increases_with_node_scale():
    elements = {
        "2": make_node("2", 250.0, -250.0),
        "3": make_node("3", 250.0, -250.0),
    }

    normal = separate_coincident_nodes(elements, node_scale=1.0)
    enlarged = separate_coincident_nodes(elements, node_scale=2.0)

    normal_distance = abs(normal["3"]["position"]["x"] - normal["2"]["position"]["x"])
    enlarged_distance = abs(enlarged["3"]["position"]["x"] - enlarged["2"]["position"]["x"])

    assert normal_distance == 100.0
    assert enlarged_distance == 175.0


def test_scaling_does_not_accumulate_offsets():
    elements = {
        "2": make_node("2", 250.0, -250.0),
        "3": make_node("3", 250.0, -250.0),
    }

    first = separate_coincident_nodes(elements, node_scale=1.0)
    separate_coincident_nodes(elements, node_scale=2.0)
    restored = separate_coincident_nodes(elements, node_scale=1.0)

    assert restored == first


def test_scaled_positions_preserve_branch_connectivity():
    elements = {
        "1": make_node("1", 0.0, -250.0),
        "2": make_node("2", 250.0, -250.0),
        "3": make_node("3", 250.0, -250.0),
        "4": make_node("4", 500.0, -250.0),
        "5": make_line("5", "1", "2"),
        "6": make_line("6", "3", "4"),
    }

    result = separate_coincident_nodes(elements, node_scale=2.0)

    assert result["5"] == elements["5"]
    assert result["6"] == elements["6"]
    assert result["2"]["position"] != result["3"]["position"]
