# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for F01 electrical quantity availability."""

import numpy as np
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.app import (
    _get_electrical_quantity_controls,
)
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    get_available_node_quantities,
)


def test_both_node_quantities_available():
    output = {
        ComponentType.node: np.zeros(
            (2, 2),
            dtype=[
                ("id", "i4"),
                ("u_pu", "f8"),
                ("u_angle", "f8"),
            ],
        )
    }

    assert get_available_node_quantities(output) == {
        "u_pu",
        "u_angle",
    }


def test_voltage_angle_unavailable_when_field_missing():
    output = {
        ComponentType.node: np.zeros(
            (2, 2),
            dtype=[
                ("id", "i4"),
                ("u_pu", "f8"),
            ],
        )
    }

    assert get_available_node_quantities(output) == {"u_pu"}


def test_no_node_output_has_no_available_quantities():
    assert get_available_node_quantities(None) == set()
    assert get_available_node_quantities({}) == set()


def test_no_scenarios_has_no_available_quantities():
    output = {
        ComponentType.node: np.zeros(
            (0, 2),
            dtype=[
                ("id", "i4"),
                ("u_pu", "f8"),
                ("u_angle", "f8"),
            ],
        )
    }

    assert get_available_node_quantities(output) == set()


def _quantity_options(scenario_count, available_quantities):
    """Extract the quantity dropdown options from the control panel."""
    panel = _get_electrical_quantity_controls(
        scenario_count,
        available_quantities,
    )

    controls_grid = panel.children[0]
    quantity_field = controls_grid.children[0]
    dropdown_container = quantity_field.children[1]
    dropdown = dropdown_container.children

    return {option["value"]: option for option in dropdown.options}


def test_both_available_quantities_are_enabled():
    options = _quantity_options(
        scenario_count=2,
        available_quantities={"u_pu", "u_angle"},
    )

    assert options["u_pu"]["disabled"] is False
    assert options["u_angle"]["disabled"] is False


def test_missing_voltage_angle_is_disabled():
    options = _quantity_options(
        scenario_count=2,
        available_quantities={"u_pu"},
    )

    assert options["u_pu"]["disabled"] is False
    assert options["u_angle"]["disabled"] is True


def test_no_available_quantities_are_disabled():
    options = _quantity_options(
        scenario_count=2,
        available_quantities=set(),
    )

    assert options["u_pu"]["disabled"] is True
    assert options["u_angle"]["disabled"] is True
    assert options["none"].get("disabled", False) is False
