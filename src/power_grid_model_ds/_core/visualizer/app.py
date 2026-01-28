# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_bootstrap_components.icons import FONT_AWESOME
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.callbacks import (  # noqa: F401  # pylint: disable=unused-import
    config,
    element_selection,
    header,
    search_form,
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.graph_layout import LayoutOptions
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_element_data
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
            ComponentType.node: grid.node.columns,
            ComponentType.line: grid.line.columns,
            ComponentType.link: grid.link.columns,
            ComponentType.transformer: grid.transformer.columns,
            ComponentType.three_winding_transformer: grid.three_winding_transformer.columns,
            ComponentType.asym_line: grid.asym_line.columns,
            ComponentType.generic_branch: grid.generic_branch.columns,
            ComponentType.sym_load: grid.sym_load.columns,
            ComponentType.sym_gen: grid.sym_gen.columns,
            ComponentType.source: grid.source.columns,
            ComponentType.sym_power_sensor: grid.sym_power_sensor.columns,
            ComponentType.asym_power_sensor: grid.asym_power_sensor.columns,
            ComponentType.sym_voltage_sensor: grid.sym_voltage_sensor.columns,
            ComponentType.asym_voltage_sensor: grid.asym_voltage_sensor.columns,
            ComponentType.sym_current_sensor: grid.sym_current_sensor.columns,
            ComponentType.asym_current_sensor: grid.asym_current_sensor.columns,
            ComponentType.transformer_tap_regulator: grid.transformer_tap_regulator.columns,
            "branch": grid.branches.columns,
        },
    )


def get_app_layout(grid: Grid) -> html.Div:
    """Get the app layout."""
    columns_store = _get_columns_store(grid)
    layout = _get_graph_layout(grid.node)
    viz_elements_dict, viz_to_comp_data = parse_element_data(grid)
    elements = list(viz_elements_dict.values())
    cytoscape_html = get_cytoscape_html(layout, elements)

    return html.Div(
        [
            columns_store,
            dcc.Store(id="parsed-elements-store", data=elements),
            dcc.Store(id="viz-to-comp-store", data=viz_to_comp_data),
            dcc.Store(id="stylesheet-store", data=DEFAULT_STYLESHEET),
            dcc.Store(id="show-appliances-store", data=True, storage_type="session"),
            HEADER_HTML,
            html.Hr(style={"border-color": "white", "margin": "0"}),
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
        ],
    )


def _get_graph_layout(nodes: NodeArray) -> LayoutOptions:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return LayoutOptions.PRESET
    return LayoutOptions.BREADTHFIRST
