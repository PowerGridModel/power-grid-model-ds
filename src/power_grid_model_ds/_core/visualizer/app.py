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
    get_available_scalar_attributes,
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
    available_attributes: dict[str, list[str]],
) -> html.Section:
    """Build independent component/attribute controls for scalar output heatmaps."""
    components = sorted(available_attributes)
    fields = [
        (
            "Component",
            "electrical-component-dropdown",
            dcc.Dropdown(
                id="electrical-component-dropdown",
                options=[{"label": name.replace("_", " ").title(), "value": name} for name in components],
                value=None,
                placeholder="Select component",
                clearable=True,
                disabled=not components,
            ),
        ),
        (
            "Attribute",
            "electrical-quantity-dropdown",
            dcc.Dropdown(
                id="electrical-quantity-dropdown",
                options=[],
                value=None,
                placeholder="Select attribute",
                clearable=True,
                disabled=True,
            ),
        ),
        (
            "Scenario (1-based)",
            "electrical-scenario-input",
            dcc.Input(
                id="electrical-scenario-input",
                type="number",
                step=1,
                value=None,
                placeholder="Scenario number",
                disabled=scenario_count == 0,
            ),
        ),
    ]
    controls = []
    for label, control_id, control in fields:
        children = [
            html.Label(label, htmlFor=control_id, className="electrical-control-label"),
            html.Div(control, className="electrical-dropdown-container"),
        ]
        if control_id == "electrical-scenario-input":
            children.append(
                html.Div(
                    [
                        html.Div(className="electrical-scenario-callout-arrow"),
                        html.Div(
                            [
                                html.Span("!", className="electrical-scenario-warning-icon", **{"aria-hidden": "true"}),
                                html.Div(
                                    [
                                        html.Strong("Invalid scenario", className="electrical-scenario-warning-title"),
                                        html.Div(id="electrical-scenario-warning-text"),
                                    ],
                                    className="electrical-scenario-warning-body",
                                ),
                            ],
                            className="electrical-scenario-warning-row",
                        ),
                    ],
                    id="electrical-scenario-warning",
                    className="electrical-scenario-warning",
                    role="alert",
                    style={"display": "none"},
                )
            )
        controls.append(
            html.Div(
                children,
                className="electrical-control-field electrical-scenario-anchor"
                if control_id == "electrical-scenario-input"
                else "electrical-control-field",
            )
        )
    return html.Section(
        [
            dcc.Store(id="electrical-available-attributes", data=available_attributes),
            html.Div(controls, className="electrical-controls-grid"),
            dcc.Store(id="electrical-scenario-count", data=scenario_count),
            html.Div(
                "",
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
    available_attributes = get_available_scalar_attributes(output_data)

    electrical_controls = _get_electrical_quantity_controls(
        scenario_count,
        available_attributes,
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
