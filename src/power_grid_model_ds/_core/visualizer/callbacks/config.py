# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import BRANCH_WIDTH, NODE_SIZE
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
    if node_scale == 1 and edge_scale == 1:
        raise PreventUpdate
    new_stylesheet = stylesheet.copy()
    edge_style = {
        "selector": "edge",
        "style": {
            "width": BRANCH_WIDTH * edge_scale,
        },
    }
    new_stylesheet.append(edge_style)
    node_style = {
        "selector": "node",
        "style": {
            "height": NODE_SIZE * node_scale,
            "width": NODE_SIZE * node_scale,
        },
    }
    new_stylesheet.append(node_style)

    return new_stylesheet, new_stylesheet


@callback(Output("cytoscape-graph", "layout"), Input("dropdown-update-layout", "value"), prevent_initial_call=True)
def update_layout(layout):
    """Callback to update the layout of the graph."""
    return {"name": layout, "animate": True}


@callback(
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("show-arrows", "value"),
    State("cytoscape-graph", "stylesheet"),
    prevent_initial_call=True,
)
def update_arrows(show_arrows, current_stylesheet):
    """Callback to update the arrow style of edges in the graph."""
    selectors = [rule["selector"] for rule in current_stylesheet]
    index = selectors.index("edge")
    edge_style = current_stylesheet[index]["style"]

    edge_style["target-arrow-shape"] = "triangle" if show_arrows else "none"
    return current_stylesheet
