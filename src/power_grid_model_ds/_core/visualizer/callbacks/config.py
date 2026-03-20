# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import BRANCH_WIDTH, NODE_SIZE
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
def scale_elements(node_scale: float, edge_scale: float, stylesheet: STYLESHEET) -> tuple[STYLESHEET, STYLESHEET]:
    """Callback to scale the elements of the graph."""
    if stylesheet is None:
        raise PreventUpdate
    new_stylesheet = stylesheet.copy()

    for selector, new_style in [
        (f".{StyleClass.BRANCH.value}", {"width": BRANCH_WIDTH * edge_scale}),
        (f".{StyleClass.NODE.value}", {"height": NODE_SIZE * node_scale, "width": NODE_SIZE * node_scale}),
        (
            f".{StyleClass.APPLIANCE_GHOST_NODE.value}",
            {"height": NODE_SIZE * node_scale * 0.25, "width": NODE_SIZE * node_scale * 0.25},
        ),
        (f".{StyleClass.GENERATING_APPLIANCE.value}", {"width": BRANCH_WIDTH * edge_scale * 0.5}),
        (f".{StyleClass.LOADING_APPLIANCE.value}", {"width": BRANCH_WIDTH * edge_scale * 0.5}),
    ]:
        new_stylesheet.append({"selector": selector, "style": new_style})

    return new_stylesheet, new_stylesheet


@callback(
    Output("cytoscape-graph", "layout"),
    Input("dropdown-update-layout", "value"),
    State("source-available-store", "data"),
    prevent_initial_call=True,
)
def update_layout(layout, source_available):
    """Callback to update the layout of the graph."""
    layout_config = layout_with_config(layout, source_available)
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
    Output("cytoscape-graph", "elements"),
    Output("show-appliances-store", "data"),
    Input("show-appliances", "value"),
    State("parsed-elements-store", "data"),
    prevent_initial_call=True,  # allow appliances to be hidden by default based on the initial value of the checkbox
)
def update_appliances(show_appliances, parsed_elements):
    """Callback to add or remove appliances in the graph."""
    if show_appliances:
        return list(parsed_elements.values()), True
    return filter_out_appliances(parsed_elements.values()), False
