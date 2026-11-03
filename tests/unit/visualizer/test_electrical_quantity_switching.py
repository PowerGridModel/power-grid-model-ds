# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for F01 electrical quantity switching."""

from unittest.mock import patch

import numpy as np
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.callbacks.config import (
    update_appliances,
)


def _make_output():
    """Create controlled batch output with two distinct node quantities."""
    node_output = np.zeros(
        (2, 2),
        dtype=[
            ("id", "i4"),
            ("u_pu", "f8"),
            ("u_angle", "f8"),
        ],
    )

    node_output["id"] = [[1, 2], [1, 2]]
    node_output["u_pu"] = [
        [0.98, 1.02],
        [0.96, 1.04],
    ]
    node_output["u_angle"] = [
        [-0.10, 0.15],
        [-0.20, 0.25],
    ]

    return {ComponentType.node: node_output}


def _make_elements():
    """Create a minimal parsed network with two nodes and one edge."""
    return {
        "node-1": {
            "data": {
                "id": "node-1",
                "group": "node",
                "associated_ids": {"node": [1]},
            }
        },
        "node-2": {
            "data": {
                "id": "node-2",
                "group": "node",
                "associated_ids": {"node": [2]},
            }
        },
        "edge-1": {
            "data": {
                "id": "edge-1",
                "source": "node-1",
                "target": "node-2",
                "group": "line",
            }
        },
    }


def _node_values(elements):
    """Return displayed electrical values indexed by Cytoscape element ID."""
    return {
        element["data"]["id"]: element["data"]["electrical_value"]
        for element in elements
        if element["data"]["id"] in {"node-1", "node-2"}
    }


def _legend_title(legend):
    """Return the text of the legend heading."""
    return legend.children[0].children


def test_switching_quantity_updates_values_and_legend():
    output = _make_output()
    parsed_elements = _make_elements()

    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.config.server_state.get_output_data",
        return_value=output,
    ):
        voltage_elements, voltage_legend = update_appliances(
            show_appliances=False,
            quantity="u_pu",
            scenario_index=1,
            parsed_elements=parsed_elements,
        )

        angle_elements, angle_legend = update_appliances(
            show_appliances=False,
            quantity="u_angle",
            scenario_index=1,
            parsed_elements=parsed_elements,
        )

    assert _node_values(voltage_elements) == {
        "node-1": 0.96,
        "node-2": 1.04,
    }

    assert _node_values(angle_elements) == {
        "node-1": -0.20,
        "node-2": 0.25,
    }

    assert _legend_title(voltage_legend) == ("Voltage magnitude (p.u.) - Scenario 2")

    assert _legend_title(angle_legend) == ("Voltage angle (rad) - Scenario 2")

    # Quantity switching must preserve the network topology.
    assert {element["data"]["id"] for element in voltage_elements} == {
        element["data"]["id"] for element in angle_elements
    }

    # The original parsed topology must not acquire electrical values.
    assert all("electrical_value" not in element["data"] for element in parsed_elements.values())


def test_missing_node_value_is_not_displayed_as_valid():
    """A node without a finite result must be marked as missing."""
    output = _make_output()

    # Make the second node's voltage angle unavailable in scenario 2.
    output[ComponentType.node]["u_angle"][1, 1] = np.nan

    parsed_elements = _make_elements()

    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.config.server_state.get_output_data",
        return_value=output,
    ):
        elements, legend = update_appliances(
            show_appliances=False,
            quantity="u_angle",
            scenario_index=1,
            parsed_elements=parsed_elements,
        )

    node_data = {
        element["data"]["id"]: element["data"] for element in elements if element["data"]["id"] in {"node-1", "node-2"}
    }

    assert node_data["node-1"]["electrical_value"] == -0.20

    # A missing result must not be assigned a numerical display value.
    assert "electrical_value" not in node_data["node-2"]
    assert node_data["node-2"]["electrical_color"] == "#9CA3AF"

    # The legend must report the missing node.
    statistics = legend.children[1]
    missing_statistic = statistics.children[2]
    assert missing_statistic.children[1].children == "1"
