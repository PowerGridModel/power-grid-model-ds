# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import html

from power_grid_model_ds._core.visualizer.electrical_quantity_legend import (
    build_electrical_legend,
)
from power_grid_model_ds._core.visualizer.electrical_quantity_styling import (
    apply_electrical_colors,
)


def test_voltage_angle_legend_uses_radians():
    legend = build_electrical_legend(
        scenario_index=1,
        summary={"minimum": -0.12, "maximum": 0.08, "missing_count": 0},
        quantity="u_angle",
    )

    title = next(child for child in legend.children if isinstance(child, html.H3))

    assert title.children == "Voltage angle (rad) - Scenario 2"


def test_voltage_angle_uses_existing_node_colouring():
    elements = [
        {
            "data": {
                "id": "node-1",
                "group": "node",
                "associated_ids": {"node": [1]},
            }
        },
        {
            "data": {
                "id": "node-2",
                "group": "node",
                "associated_ids": {"node": [2]},
            }
        },
    ]

    coloured, summary = apply_electrical_colors(
        elements,
        "node",
        {1: -0.12, 2: 0.08},
    )

    assert summary["minimum"] == -0.12
    assert summary["maximum"] == 0.08
    assert summary["missing_count"] == 0
    assert coloured[0]["data"]["electrical_value"] == -0.12
    assert coloured[1]["data"]["electrical_value"] == 0.08
    assert coloured[0]["data"]["electrical_color"] != coloured[1]["data"]["electrical_color"]
