# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""F01 component and attribute availability."""

import numpy as np
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.app import _get_electrical_quantity_controls
from power_grid_model_ds._core.visualizer.callbacks.config import update_scenario_warning
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import get_available_scalar_attributes


def test_scalar_attributes_exclude_vectors_and_non_float_fields():
    output = {
        ComponentType.node: np.zeros(
            (2, 1),
            dtype=[
                ("id", "i4"),
                ("u_pu", "f8"),
                ("u_angle", "f8"),
                ("phase_values", "f8", (3,)),
                ("status", "i4"),
                ("complex_value", "c16"),
            ],
        )
    }
    assert get_available_scalar_attributes(output) == {"node": ["u_pu", "u_angle"]}


def test_empty_output_has_no_attributes():
    assert get_available_scalar_attributes(None) == {}
    assert get_available_scalar_attributes({}) == {}


def test_controls_use_numeric_scenario_input():
    panel = _get_electrical_quantity_controls(2000, {"node": ["u_pu"]})
    controls = panel.children[1].children
    assert controls[0].children[1].children.id == "electrical-component-dropdown"
    assert controls[1].children[1].children.id == "electrical-quantity-dropdown"
    scenario = controls[2].children[1].children
    assert scenario.id == "electrical-scenario-input"
    # Deliberately validate bounds in Dash callbacks, not HTML input constraints.
    # Otherwise browsers may coerce an invalid scenario (e.g. 0) to None.
    assert scenario.type == "number"
    assert scenario.step == 1
    assert getattr(scenario, "min", None) is None
    assert getattr(scenario, "max", None) is None


def test_missing_angle_is_not_offered():
    output = {ComponentType.node: np.zeros((2, 2), dtype=[("id", "i4"), ("u_pu", "f8")])}
    assert get_available_scalar_attributes(output) == {"node": ["u_pu"]}


def test_zero_scenarios_have_no_available_attributes():
    output = {ComponentType.node: np.zeros((0, 2), dtype=[("id", "i4"), ("u_pu", "f8"), ("u_angle", "f8")])}
    assert get_available_scalar_attributes(output) == {}


def test_no_attributes_disables_component_and_attribute_controls():
    panel = _get_electrical_quantity_controls(2, {})
    controls = panel.children[1].children
    assert controls[0].children[1].children.disabled
    assert controls[1].children[1].children.disabled


def test_scenario_zero_displays_warning():
    style, message = update_scenario_warning(0, 4)
    assert style == {"display": "block"}
    assert "Scenario 0 does not exist" in message


def test_valid_scenario_hides_warning():
    style, message = update_scenario_warning(1, 4)
    assert style == {"display": "none"}
    assert message == ""


def test_default_legend_is_empty():
    panel = _get_electrical_quantity_controls(4, {"node": ["u_pu"]})
    assert panel.children[3].children == ""
