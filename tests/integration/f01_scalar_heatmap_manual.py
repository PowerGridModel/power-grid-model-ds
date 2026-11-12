# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Manual F01 browser fixture with symmetric, scalar batch output.

Run from the repository root:
    python -m tests.integration.f01_scalar_heatmap_manual

The existing asymmetric visualizer integration fixture is deliberately unchanged.
This fixture supplies illustrative output values; it does not run a power flow.
"""

import numpy as np
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    get_available_scalar_attributes,
    get_scenario_count,
)
from power_grid_model_ds.visualizer import visualize
from tests.integration.visualizer_tests import get_coordinated_three_phase_grid


def visualize_f01_scalar_heatmap() -> None:
    """Open a grid with four scenarios and scalar node/line attributes."""
    grid = get_coordinated_three_phase_grid()
    scenario_count = 4
    output_data = {}

    for component, component_ids in (
        (ComponentType.node, grid.node.id),
        (ComponentType.line, grid.line.id),
    ):
        array = initialize_array(DatasetType.sym_output, component, (scenario_count, len(component_ids)))
        array["id"] = np.broadcast_to(component_ids, (scenario_count, len(component_ids)))
        # Fill only floating-point scalar fields. Other fields retain library defaults.
        for field in array.dtype.names or ():
            field_dtype = array.dtype.fields[field][0]
            if field != "id" and field_dtype.subdtype is None and field_dtype.kind == "f":
                array[field] = np.array(
                    [[float((scenario + 1) * 10 + index + 1) for index in range(len(component_ids))]
                     for scenario in range(scenario_count)],
                    dtype=float,
                )
        output_data[component] = array

    available = get_available_scalar_attributes(output_data)
    print("F01 scenario count:", get_scenario_count(output_data), flush=True)
    print("F01 available attributes:", available, flush=True)
    if not available:
        raise RuntimeError("Fixture unexpectedly contains no eligible scalar output attributes")
    print("F01: select Component, Attribute and scenario 1–4 in the browser", flush=True)
    print("F01: verify legend, colours, scenario switching, and component switching", flush=True)
    print("F01: values are illustrative, not calculated electrical results", flush=True)
    visualize(grid=grid, output_data=output_data, debug=True)


if __name__ == "__main__":
    visualize_f01_scalar_heatmap()
