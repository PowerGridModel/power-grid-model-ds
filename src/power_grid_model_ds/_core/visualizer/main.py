import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_bootstrap_components.icons import FONT_AWESOME

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.callbacks import (  # noqa: F401  # pylint: disable=unused-import
    element_scaling,
    element_selection,
    layout_dropdown,
    search_form,
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_branches, parse_node_array
from power_grid_model_ds.arrays import NodeArray

GOOGLE_FONTS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
MDBOOTSTRAP = "https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/8.2.0/mdb.min.css"


def visualize(grid: Grid, debug: bool = False):
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
    columns_store = _get_columns_store(grid)
    layout = _get_layout(grid.node)
    elements = parse_node_array(grid.node) + parse_branches(grid)
    cytoscape_html = get_cytoscape_html(layout, elements)

    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, MDBOOTSTRAP, FONT_AWESOME, GOOGLE_FONTS]
    )
    app.layout = html.Div(
        [
            columns_store,
            HEADER_HTML,
            html.Hr(style={"border-color": "white", "margin": "0"}),
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
        ],
    )
    app.run(debug=debug)


def _get_columns_store(grid: Grid) -> dcc.Store:
    return dcc.Store(
        id="columns-store",
        data={
            "node": grid.node.columns,
            "line": grid.line.columns,
            "link": grid.link.columns,
            "transformer": grid.transformer.columns,
            "branch": grid.branches.columns,
        },
    )


def _get_layout(nodes: NodeArray) -> str:
    """Determine the layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return "preset"
    return "breadthfirst"
