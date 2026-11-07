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
from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    extract_scenario_values,
    get_available_scalar_attributes,
    get_scenario_count,
)
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
    Output("electrical-quantity-dropdown", "options"),
    Output("electrical-quantity-dropdown", "value"),
    Output("electrical-quantity-dropdown", "disabled"),
    Input("electrical-component-dropdown", "value"),
    State("electrical-available-attributes", "data"),
)
def update_electrical_attributes(component, available_attributes):
    """Offer only scalar output attributes of the selected component."""
    attributes = (available_attributes or {}).get(component, [])
    options = [{"label": name, "value": name} for name in attributes]
    return options, None, not bool(options)


def _scenario_validation_message(value, count):
    """Return a warning for invalid user input, or None when valid."""
    if not count:
        return None
    if value is None or value == "":
        return f"Enter a whole-number scenario between 1 and {count}."
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return f"Enter a whole-number scenario between 1 and {count}."
    if not float(value).is_integer():
        return f"Scenario must be a whole number between 1 and {count}."
    if not 1 <= value <= count:
        return f"Scenario {int(value)} does not exist. Available scenarios: 1-{count}."
    return None


@callback(
    Output("electrical-scenario-warning", "style"),
    Output("electrical-scenario-warning-text", "children"),
    Input("electrical-scenario-input", "value"),
    State("electrical-scenario-count", "data"),
)
def update_scenario_warning(value, scenario_count):
    """Show a floating warning only when a nonempty scenario is invalid."""
    if value is None or value == "":
        return {"display": "none"}, ""
    message = _scenario_validation_message(value, scenario_count)
    return ({"display": "none"} if message is None else {"display": "block"}), message or ""


@callback(
    Output("cytoscape-graph", "elements"),
    Output("electrical-quantity-legend", "children"),
    Input("show-appliances-store", "data"),
    Input("electrical-component-dropdown", "value"),
    Input("electrical-quantity-dropdown", "value"),
    Input("electrical-scenario-input", "value"),
    State("parsed-elements-store", "data"),
)
def update_appliances(show_appliances, component, quantity, scenario_number, parsed_elements):
    """Colour a selected component's scalar output for a one-based scenario."""
    if parsed_elements is None:
        raise PreventUpdate

    elements = list(parsed_elements.values()) if show_appliances else filter_out_appliances(parsed_elements.values())
    if not component or not quantity:
        return clear_electrical_colors(elements), ""
    if scenario_number is None:
        return clear_electrical_colors(elements), "Select a scenario to display electrical values."

    output_data = server_state.get_output_data()
    available = get_available_scalar_attributes(output_data)
    if quantity not in available.get(component, []):
        return clear_electrical_colors(elements), "The selected attribute is unavailable."

    scenario_count = get_scenario_count(output_data)
    if (
        isinstance(scenario_number, bool)
        or not isinstance(scenario_number, (int, float))
        or not float(scenario_number).is_integer()
        or not 1 <= scenario_number <= scenario_count
    ):
        return clear_electrical_colors(elements), f"Enter a scenario between 1 and {scenario_count}."

    values = extract_scenario_values(output_data, ComponentType(component), quantity, int(scenario_number) - 1)
    colored_elements, summary = apply_electrical_colors(elements, component, values)
    legend_content = build_electrical_legend(
        scenario_index=int(scenario_number) - 1,
        summary=summary,
        quantity=quantity,
        component_group=component,
    )
    return colored_elements, legend_content
