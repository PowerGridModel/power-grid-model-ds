# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import (
    BRANCH_WIDTH,
    NODE_SIZE,
    SELECTOR_APPLIANCE_GHOST_NODE,
    SELECTOR_BRANCH,
    SELECTOR_GENERATING_EDGE,
    SELECTOR_LOADING_EDGE,
    SELECTOR_NODES,
)
from power_grid_model_ds._core.visualizer.layout.graph_layout import LayoutOptions
from power_grid_model_ds._core.visualizer.typing import STYLESHEET


@callback(
    Output("stylesheet-store", "data", allow_duplicate=True),
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("node-scale-input", "value"),
    Input("edge-scale-input", "value"),
    State("stylesheet-store", "data"),
    prevent_initial_call=True,
)
def scale_elements(node_scale: float, edge_scale: float, stylesheet: STYLESHEET) -> tuple[STYLESHEET, STYLESHEET]:
    """Callback to scale the elements of the graph."""
    if stylesheet is None:
        raise PreventUpdate
    new_stylesheet = stylesheet.copy()

    for selector, new_style in [
        (SELECTOR_BRANCH, {"width": BRANCH_WIDTH * edge_scale}),
        (SELECTOR_NODES, {"height": NODE_SIZE * node_scale, "width": NODE_SIZE * node_scale}),
        (
            SELECTOR_APPLIANCE_GHOST_NODE,
            {"height": NODE_SIZE * 0.25 * node_scale, "width": NODE_SIZE * 0.25 * node_scale},
        ),
        (SELECTOR_GENERATING_EDGE, {"width": BRANCH_WIDTH * 0.5 * edge_scale}),
        (SELECTOR_LOADING_EDGE, {"width": BRANCH_WIDTH * 0.5 * edge_scale}),
    ]:
        new_stylesheet.append({"selector": selector, "style": new_style})

    return new_stylesheet, new_stylesheet


@callback(Output("cytoscape-graph", "layout"), Input("dropdown-update-layout", "value"), prevent_initial_call=True)
def update_layout(layout_config):
    """Callback to update the layout of the graph."""
    layout_config = LayoutOptions(layout_config).layout_with_config()
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
    index = selectors.index(SELECTOR_BRANCH)
    edge_style = current_stylesheet[index]["style"]

    edge_style["target-arrow-shape"] = "triangle" if show_arrows else "none"
    return current_stylesheet


@callback(
    Output("cytoscape-graph", "elements"),
    Output("show-appliances-store", "data"),
    Input("show-appliances", "value"),
    State("parsed-elements-store", "data"),
    prevent_initial_call=True,
)
def update_appliances(show_appliances, parsed_elements):
    """Callback to add or remove appliances in the graph."""
    if show_appliances:
        return parsed_elements, True
    return [
        element
        for element in parsed_elements
        if element["data"]["group"] not in ["sym_load", "sym_gen", "sym_load_ghost_node", "sym_gen_ghost_node"]
    ], False
