# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.electrical_quantity_legend import build_electrical_legend
from power_grid_model_ds._core.visualizer.electrical_quantity_styling import (
    apply_electrical_colors,
    clear_electrical_colors,
)
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import extract_scenario_values
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import BRANCH_WIDTH, NODE_SIZE
from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions
from power_grid_model_ds._core.visualizer.layout.layout_config import layout_with_config
from power_grid_model_ds._core.visualizer.parsing_utils import filter_out_appliances
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass
from power_grid_model_ds._core.visualizer.typing import STYLESHEET


@callback(
    Output("stylesheet-store", "data", allow_duplicate=True),
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("node-scale-input", "value"),
    Input("edge-scale-input", "value"),
    State("stylesheet-store", "data"),
    prevent_initial_call=True,
)
def scale_elements(
    node_scale: float,
    edge_scale: float,
    stylesheet: STYLESHEET,
) -> tuple[STYLESHEET, STYLESHEET]:
    """Callback to scale the elements of the graph."""
    if stylesheet is None:
        raise PreventUpdate

    new_stylesheet = stylesheet.copy()

    for selector, new_style in [
        (f".{StyleClass.BRANCH.value}", {"width": BRANCH_WIDTH * edge_scale}),
        (
            f".{StyleClass.NODE.value}",
            {
                "height": NODE_SIZE * node_scale,
                "width": NODE_SIZE * node_scale,
            },
        ),
        (
            f".{StyleClass.APPLIANCE_GHOST_NODE.value}",
            {
                "height": NODE_SIZE * node_scale * 0.25,
                "width": NODE_SIZE * node_scale * 0.25,
            },
        ),
        (
            f".{StyleClass.GENERATING_APPLIANCE.value}",
            {"width": BRANCH_WIDTH * edge_scale * 0.5},
        ),
        (
            f".{StyleClass.LOADING_APPLIANCE.value}",
            {"width": BRANCH_WIDTH * edge_scale * 0.5},
        ),
    ]:
        new_stylesheet.append(
            {
                "selector": selector,
                "style": new_style,
            }
        )

    return new_stylesheet, new_stylesheet


@callback(
    Output("cytoscape-graph", "layout"),
    Input("dropdown-update-layout", "value"),
    State("source-available-store", "data"),
    prevent_initial_call=True,
)
def update_layout(layout: str, source_available: bool):
    """Callback to update the layout of the graph."""
    if not layout:
        raise PreventUpdate

    layout_config = layout_with_config(
        LayoutOptions(layout),
        source_available,
    )
    layout_config.update({"animate": True})
    return layout_config


@callback(
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("show-arrows", "value"),
    State("cytoscape-graph", "stylesheet"),
    prevent_initial_call=True,
)
def update_arrows(show_arrows, current_stylesheet):
    """Callback to update the arrow style of edges in the graph."""
    selectors = [rule["selector"] for rule in current_stylesheet]
    index = selectors.index(f".{StyleClass.BRANCH.value}")
    edge_style = current_stylesheet[index]["style"]

    edge_style["target-arrow-shape"] = "triangle" if show_arrows else "none"
    return current_stylesheet


@callback(
    Output("show-appliances-store", "data"),
    Input("show-appliances", "value"),
)
def update_appliance_visibility(show_appliances):
    """Store appliance visibility independently of electrical colouring."""
    return bool(show_appliances)


@callback(
    Output("cytoscape-graph", "elements"),
    Output("electrical-quantity-legend", "children"),
    Input("show-appliances-store", "data"),
    Input("electrical-quantity-dropdown", "value"),
    Input("electrical-scenario-dropdown", "value"),
    State("parsed-elements-store", "data"),
)
def update_appliances(
    show_appliances,
    quantity,
    scenario_index,
    parsed_elements,
):
    """Compose graph elements using appliance visibility and electrical values."""
    if parsed_elements is None:
        raise PreventUpdate

    # Rebuild visible elements from the original parsed topology.
    # Do not reuse elements that may contain previous electrical colours.
    elements = list(parsed_elements.values()) if show_appliances else filter_out_appliances(parsed_elements.values())

    # Reset electrical colouring when no quantity is selected.
    if quantity in (None, "none"):
        return (
            clear_electrical_colors(elements),
            "No electrical quantity selected.",
        )

    # A quantity alone is insufficient: a scenario must also be selected.
    if scenario_index is None:
        return (
            clear_electrical_colors(elements),
            "Select a scenario to display electrical values.",
        )

    # F01 supports two node quantities.
    if quantity not in ("u_pu", "u_angle"):
        raise ValueError(f"Unsupported electrical quantity: {quantity}")

    values = extract_scenario_values(
        server_state.get_output_data(),
        ComponentType.node,
        quantity,
        scenario_index,
    )

    colored_elements, legend = apply_electrical_colors(
        elements,
        ComponentType.node.value,
        values,
    )

    legend_content = build_electrical_legend(
        scenario_index=scenario_index,
        minimum=legend["minimum"],
        maximum=legend["maximum"],
        missing_count=legend["missing_count"],
        quantity=quantity,
    )

    return colored_elements, legend_content
