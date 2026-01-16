# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_bootstrap_components.icons import FONT_AWESOME

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.callbacks import (  # noqa: F401  # pylint: disable=unused-import
    config,
    element_selection,
    header,
    search_form,
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_element_data
from power_grid_model_ds._core.visualizer.typing import VizToComponentData
from power_grid_model_ds.arrays import NodeArray

GOOGLE_FONTS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
MDBOOTSTRAP = "https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/8.2.0/mdb.min.css"


def visualize(grid: Grid, debug: bool = False, port: int = 8050) -> None:
    """Visualize the Grid.

    grid: Grid
        The grid to visualize.

    layout: str
        The layout to use.

        If 'layout' is not provided (""):
            And grid.node contains "x" and "y" columns:
                The layout will be set to "preset" which uses the x and y coordinates to place the nodes.
            Otherwise:
                The layout will be set to "breadthfirst", which is a hierarchical breadth-first-search (BFS) layout.
        Other options:
            - "random": A layout that places the nodes randomly.
            - "circle": A layout that places the nodes in a circle.
            - "concentric": A layout that places the nodes in concentric circles.
            - "grid": A layout that places the nodes in a grid matrix.
            - "cose": A layout that uses the CompoundSpring Embedder algorithm (force-directed layout)
    """

    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, MDBOOTSTRAP, FONT_AWESOME, GOOGLE_FONTS]
    )
    app.layout = get_app_layout(grid)
    app.run(debug=debug, port=port)


def _get_columns_store(grid: Grid) -> dcc.Store:
    return dcc.Store(
        id="columns-store",
        data={
            "node": grid.node.columns,
            "line": grid.line.columns,
            "link": grid.link.columns,
            "transformer": grid.transformer.columns,
            "three_winding_transformer": grid.three_winding_transformer.columns,
            "branch": grid.branches.columns,
            "sym_load": grid.sym_load.columns,
            "sym_gen": grid.sym_gen.columns,
            "source": grid.source.columns,
            "sym_power_sensor": grid.sym_power_sensor.columns,
            "sym_voltage_sensor": grid.sym_voltage_sensor.columns,
            "transformer_tap_regulator": grid.transformer_tap_regulator.columns,
        },
    )


def _get_viz_to_comp_store(viz_to_comp_data: VizToComponentData) -> dcc.Store:
    """Create a store for all data mapped by visualization element to component data."""
    return dcc.Store(id="viz-to-comp-store", data=viz_to_comp_data)


def get_app_layout(grid: Grid) -> html.Div:
    """Get the app layout."""
    columns_store = _get_columns_store(grid)
    elements, viz_to_comp_data = parse_element_data(grid)
    graph_layout = _get_graph_layout(grid.node)
    viz_to_comp_store = _get_viz_to_comp_store(viz_to_comp_data)
    cytoscape_html = get_cytoscape_html(graph_layout, elements)

    return html.Div(
        [
            columns_store,
            viz_to_comp_store,
            dcc.Store(id="stylesheet-store", data=DEFAULT_STYLESHEET),
            HEADER_HTML,
            html.Hr(style={"border-color": "white", "margin": "0"}),
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
        ],
    )


def _get_graph_layout(nodes: NodeArray):
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return {"name": "preset"}
    return {"name": "breadthfirst", "roots": 'node[group = "source_ghost_node"]'}
    # TODO (nitbharambe) Add layout params after config option is used
    # TODO (nitbharambe) Experiment with different layout parameters (Remove comments)
    # return {'name': 'cose', 'nodeOverlap': '1000', 'gravity': 100}
    # return {'name': 'cose',  "nodeRepulsion": "function( node ){ return 12048; }"}
