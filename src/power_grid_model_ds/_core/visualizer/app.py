# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html
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
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.layout_config import get_default_graph_layout
from power_grid_model_ds._core.visualizer.layout.node_overlap import separate_coincident_nodes
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_GRAPH_HTML, SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_element_data
from power_grid_model_ds._core.visualizer.parsing_utils import filter_out_appliances

GOOGLE_FONTS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
MDBOOTSTRAP = "https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/8.2.0/mdb.min.css"


def _get_columns_store(grid: Grid) -> dcc.Store:
    """Store the available columns for each grid component type."""
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
            "branches": grid.branches.columns,
        },
    )


def get_app_layout(grid: Grid) -> html.Div:
    """Create the visualiser layout for the supplied Grid."""
    columns_store = _get_columns_store(grid)

    # Select the initial layout based on the available node coordinates.
    layout = get_default_graph_layout(grid.node)

    # Preserve the original parsed elements and their coordinates.
    # These elements are the source for subsequent display recalculations.
    viz_elements_dict = parse_element_data(grid)

    # Resolve coincident electrical nodes for the initial display.
    # The default node scale is 1.0.
    display_elements_dict = separate_coincident_nodes(
        viz_elements_dict,
        node_scale=1.0,
    )

    # Appliances are hidden initially.
    initial_elements = filter_out_appliances(display_elements_dict.values())

    cytoscape_html = get_cytoscape_html(
        layout,
        initial_elements,
        grid.source.size != 0,
    )

    return html.Div(
        [
            columns_store,
            # Keep original positions for scale-dependent recalculation.
            dcc.Store(
                id="parsed-elements-store",
                data=viz_elements_dict,
            ),
            dcc.Store(
                id="node-position-state-store",
                data={
                    "scale": 1.0,
                    "manual_positions": {},
                },
            ),
            dcc.Store(
                id="stylesheet-store",
                data=DEFAULT_STYLESHEET,
            ),
            dcc.Store(
                id="source-available-store",
                data=grid.source.size != 0,
            ),
            dcc.Store(
                id="show-appliances-store",
                data=False,
                storage_type="session",
            ),
            HEADER_HTML,
            html.Hr(
                style={"border-color": "white", "margin": "0"},
            ),
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
            SELECTION_GRAPH_HTML,
        ],
    )
