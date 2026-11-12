# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generic F01 component colouring cases."""

import numpy as np
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.electrical_quantity_styling import apply_electrical_colors
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    extract_scenario_values,
    get_available_scalar_attributes,
)


def test_line_output_colours_line_edges():
    lines = np.zeros((1, 2), dtype=[("id", "i4"), ("loading", "f8")])
    lines["id"] = [[10, 11]]
    lines["loading"] = [[0.2, 0.8]]
    output = {ComponentType.line: lines}
    assert get_available_scalar_attributes(output) == {"line": ["loading"]}
    values = extract_scenario_values(output, ComponentType.line, "loading", 0)
    elements = [{"data": {"group": "line", "associated_ids": {"line": [i]}}} for i in (10, 11)]
    coloured, summary = apply_electrical_colors(elements, "line", values)
    assert [e["data"]["electrical_value"] for e in coloured] == [0.2, 0.8]
    assert summary["missing_count"] == 0


def test_three_winding_transformer_can_colour_multiple_edges():
    elements = [
        {"data": {"group": "three_winding_transformer", "associated_ids": {"three_winding_transformer": [17]}}}
        for _ in range(3)
    ]
    coloured, _ = apply_electrical_colors(elements, "three_winding_transformer", {17: 0.9})
    assert all(e["data"]["electrical_value"] == 0.9 for e in coloured)
