# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.styling_classification import (
    get_appliance_edge_classification,
    get_branch_classification,
    get_node_classification,
)
from power_grid_model_ds._core.visualizer.typing import STYLESHEET


@callback(
    Output("cytoscape-graph", "elements", allow_duplicate=True),
    Input("scenario-input", "value"),
    State("cytoscape-graph", "elements"),
    prevent_initial_call=True,
)
def update_selected_scenario(scenario_idx: int | None, elements) -> STYLESHEET:
    """Callback to update the selected scenario in the store.

    Args:
        scenario_idx: The scenario index from the input
        elements: The current elements from the cytoscape graph
    Returns:
        The updated elements with the new classification for the selected scenario

    Raises:
        PreventUpdate: If the scenario index is invalid
    """
    if scenario_idx is None:
        raise PreventUpdate

    grid = server_state.safe_get_grid()
    update_data = server_state.safe_get_update_data()
    output_data = server_state.safe_get_output_data()

    _update_grid_for_scenario(scenario_idx, grid, update_data, output_data)
    _update_classification_for_scenario(grid, elements)

    return elements


def _update_grid_for_scenario(scenario_idx: int, grid, update_data, output_data) -> None:
    """Helper function to update the grid data for the selected scenario.

    This function updates the grid data in the server state based on the selected scenario index.
    It applies both update_data (which may contain partial updates with different ordering)
    and output_data (which has the same ids and order as the grid).

    Args:
        scenario_idx: The index of the selected scenario
        grid: The grid object to be updated
        update_data: The update data for the scenarios
        output_data: The output data for the scenarios
    """

    if update_data is not None:
        first_array = next(iter(update_data.values()))
        if scenario_idx is None or scenario_idx < 0 or scenario_idx >= first_array.shape[0]:
            raise PreventUpdate

        for arr_name, update_arr in update_data.items():
            grid_arr = getattr(grid, arr_name)

            update_ids = update_arr[scenario_idx, :]["id"]
            indices = np.searchsorted(grid_arr.id, update_ids)

            valid = (indices < len(grid_arr.id)) & (grid_arr.id[indices] == update_ids)
            if not np.all(valid):
                raise ValueError(f"IDs {update_ids[~valid]} not found in base input data for array {arr_name}")

            for attr in update_arr.dtype.names:
                if attr in grid_arr.dtype.names and attr != "id":
                    grid_arr[attr][indices] = update_arr[scenario_idx, :][attr]

    if output_data is not None:
        first_array = next(iter(output_data.values()))
        if scenario_idx is None or scenario_idx < 0 or scenario_idx >= first_array.shape[0]:
            raise PreventUpdate

        for arr_name, output_arr in output_data.items():
            grid_arr = getattr(grid, arr_name)

            for attr in output_arr[scenario_idx, :].dtype.names:
                if attr in grid_arr.dtype.names and attr != "id":
                    grid_arr[attr][:] = output_arr[scenario_idx, :][attr]


def _update_classification_for_scenario(grid, elements) -> None:
    """Helper function to update the classification for the selected scenario."""
    # Get new classifications based on the updated grid data
    new_classifications = {}
    for comp in ComponentType:
        if not hasattr(grid, comp.value):
            continue
        grid_arr = getattr(grid, comp.value)

        if comp == ComponentType.node:
            for row in grid_arr:
                new_classifications[str(row.id.item())] = get_node_classification(row)
        elif comp in [
            ComponentType.transformer,
            ComponentType.link,
            ComponentType.generic_branch,
            ComponentType.line,
            ComponentType.asym_line,
        ]:
            for row in grid_arr:
                new_classifications[str(row.id.item())] = get_branch_classification(row, comp)  # type: ignore[arg-type]
        elif comp in [ComponentType.sym_load, ComponentType.sym_gen, ComponentType.source]:
            for row in grid_arr:
                new_classifications[str(row.id.item())] = get_appliance_edge_classification(row, comp)  # type: ignore[arg-type]
        elif comp == ComponentType.three_winding_transformer:
            for row in grid_arr.as_branches():
                for count in range(3):
                    branch3_id_str = f"{row.id.item()}_{count}"
                    new_classifications[branch3_id_str] = get_branch_classification(row, comp)

    # Assign new classifications to elements
    for element in elements:
        element_id = element["data"]["id"]
        if element_id in new_classifications:
            element["classes"] = new_classifications[element_id]
