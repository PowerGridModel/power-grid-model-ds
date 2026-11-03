# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks import (  # noqa: F401  # pylint: disable=unused-import
    config,
    element_selection,
    header,
    search_form,
)
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    get_available_node_quantities,
    get_scenario_count,
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.layout_config import get_default_graph_layout
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_GRAPH_HTML, SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_element_data
from power_grid_model_ds._core.visualizer.parsing_utils import filter_out_appliances

GOOGLE_FONTS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
MDBOOTSTRAP = "https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/8.2.0/mdb.min.css"


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
            "branches": grid.branches.columns,
        },
    )


def _get_electrical_quantity_controls(
    scenario_count: int,
    available_quantities: set[str],
) -> html.Section:
    """Build the electrical quantity controls and legend."""

    quantity_field = html.Div(
        [
            html.Label(
                "Quantity",
                htmlFor="electrical-quantity-dropdown",
                className="electrical-control-label",
            ),
            html.Div(
                dcc.Dropdown(
                    id="electrical-quantity-dropdown",
                    options=[
                        {
                            "label": "No electrical colouring",
                            "value": "none",
                        },
                        {
                            "label": "Voltage magnitude (p.u.)",
                            "value": "u_pu",
                            "disabled": "u_pu" not in available_quantities,
                        },
                        {
                            "label": "Voltage angle (rad)",
                            "value": "u_angle",
                            "disabled": "u_angle" not in available_quantities,
                        },
                    ],
                    value="none",
                    clearable=False,
                    disabled=scenario_count == 0,
                ),
                className="electrical-dropdown-container",
            ),
        ],
        className="electrical-control-field",
    )

    scenario_field = html.Div(
        [
            html.Label(
                "Scenario",
                htmlFor="electrical-scenario-dropdown",
                className="electrical-control-label",
            ),
            html.Div(
                dcc.Dropdown(
                    id="electrical-scenario-dropdown",
                    options=[{"label": f"Scenario {index + 1}", "value": index} for index in range(scenario_count)],
                    value=None,
                    placeholder="No scenario selected",
                    clearable=True,
                    disabled=scenario_count == 0,
                ),
                className="electrical-dropdown-container",
            ),
        ],
        className="electrical-control-field",
    )

    return html.Section(
        [
            html.Div(
                [
                    quantity_field,
                    html.Div(
                        className="electrical-controls-divider",
                        **{"aria-hidden": "true"},
                    ),
                    scenario_field,
                ],
                className="electrical-controls-grid",
            ),
            html.Div(
                "No electrical quantity selected.",
                id="electrical-quantity-legend",
                className="electrical-quantity-legend",
                role="status",
                **{"aria-live": "polite"},
            ),
        ],
        className="electrical-quantity-panel",
        **{"aria-label": "Electrical quantity configuration"},
    )


def get_app_layout(grid: Grid) -> html.Div:
    """Get the app layout."""
    columns_store = _get_columns_store(grid)
    layout = get_default_graph_layout(grid.node)
    viz_elements_dict = parse_element_data(grid)

    initial_elements = filter_out_appliances(viz_elements_dict.values())

    cytoscape_html = get_cytoscape_html(
        layout,
        initial_elements,
        grid.source.size != 0,
    )

    output_data = server_state.get_output_data()

    scenario_count = get_scenario_count(output_data)
    available_quantities = get_available_node_quantities(output_data)

    electrical_controls = _get_electrical_quantity_controls(
        scenario_count,
        available_quantities,
    )

    return html.Div(
        [
            columns_store,
            dcc.Store(
                id="parsed-elements-store",
                data=viz_elements_dict,
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
                style={
                    "border-color": "white",
                    "margin": "0",
                },
            ),
            electrical_controls,
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
            SELECTION_GRAPH_HTML,
        ],
    )
