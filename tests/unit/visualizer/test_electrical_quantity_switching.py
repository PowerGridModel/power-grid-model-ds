# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for F01 scalar output switching."""

from copy import deepcopy
from unittest.mock import patch

import numpy as np
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.callbacks.config import update_appliances, update_electrical_attributes


def _data():
    nodes = np.zeros((2, 2), dtype=[("id", "i4"), ("u_pu", "f8"), ("u_angle", "f8")])
    nodes["id"] = [[1, 2], [1, 2]]
    nodes["u_pu"] = [[0.98, 1.02], [0.96, 1.04]]
    nodes["u_angle"] = [[-0.1, 0.15], [-0.2, 0.25]]
    return {ComponentType.node: nodes}


def _elements():
    return {str(i): {"data": {"id": str(i), "group": "node", "associated_ids": {"node": [i]}}} for i in (1, 2)}


def test_component_change_resets_attribute():
    options, value, disabled = update_electrical_attributes("node", {"node": ["u_pu", "u_angle"]})
    assert [option["value"] for option in options] == ["u_pu", "u_angle"]
    assert value is None
    assert not disabled


def test_quantity_switching_and_one_based_scenario():
    parsed_elements = _elements()
    original_elements = deepcopy(parsed_elements)
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.config.server_state.get_output_data", return_value=_data()
    ):
        voltage, legend = update_appliances(
            show_appliances=False,
            component="node",
            quantity="u_pu",
            scenario_number=2,
            parsed_elements=parsed_elements,
        )
        angle, angle_legend = update_appliances(
            show_appliances=False,
            component="node",
            quantity="u_angle",
            scenario_number=2,
            parsed_elements=parsed_elements,
        )
    assert [e["data"]["electrical_value"] for e in voltage] == [0.96, 1.04]
    assert [e["data"]["electrical_value"] for e in angle] == [-0.2, 0.25]
    assert legend.children[0].children == "Voltage magnitude (p.u.) - Scenario 2"
    assert angle_legend.children[0].children == "Voltage angle (rad) - Scenario 2"
    assert {element["data"]["id"] for element in voltage} == {element["data"]["id"] for element in angle}
    assert parsed_elements == original_elements
    assert all("electrical_value" not in element["data"] for element in parsed_elements.values())
    assert all("electrical_color" not in element["data"] for element in parsed_elements.values())


def test_invalid_scenario_clears_colouring():
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.config.server_state.get_output_data", return_value=_data()
    ):
        elements, message = update_appliances(
            show_appliances=False,
            component="node",
            quantity="u_pu",
            scenario_number=2.5,
            parsed_elements=_elements(),
        )
    assert "Enter a scenario" in message
    assert all("electrical_value" not in e["data"] for e in elements)


def test_missing_value_is_grey():
    output = _data()
    output[ComponentType.node]["u_angle"][1, 1] = np.nan
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.config.server_state.get_output_data", return_value=output
    ):
        elements, legend = update_appliances(
            show_appliances=False,
            component="node",
            quantity="u_angle",
            scenario_number=2,
            parsed_elements=_elements(),
        )
    assert "electrical_value" not in elements[1]["data"]
    assert elements[1]["data"]["electrical_color"] == "#9CA3AF"
    assert legend.children[1].children[2].children[1].children == "1"
