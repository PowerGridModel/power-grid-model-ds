# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Selection tables, graphs, and measurement-comparison guidance."""

import math
from typing import TypedDict

from dash import Input, Output, callback, dcc, html

from power_grid_model_ds._core.visualizer.graph_action_styles import (
    GRAPH_ACTION_BUTTON_STYLE,
)

_AriaHidden = TypedDict("_AriaHidden", {"aria-hidden": str})
_ARIA_HIDDEN: _AriaHidden = {"aria-hidden": "true"}

SELECTION_OUTPUT_HEADER_STYLE = {"margin": "20px 0 10px 0"}
_SELECTION_OUTPUT_STYLE = {"overflowX": "scroll", "textAlign": "center", "margin": "10px"}

SELECTION_OUTPUT_HTML = html.Div(
    dcc.Markdown(
        "Click on a **node** or **edge** to display all its associated components and their attributes."
        "\nYou can also use Ctrl+Click (or Cmd+Click on Mac) to select multiple nodes or edges.",
        style=SELECTION_OUTPUT_HEADER_STYLE,
    ),
    id="selection-output",
    style=_SELECTION_OUTPUT_STYLE,
)

SELECTION_GRAPH_HTML = html.Div(
    [
        # Temporary cell selection used by the existing callback.
        dcc.Store(
            id="selected-selection-cell",
            storage_type="memory",
        ),
        # Explicitly retained graph selections for F14.
        dcc.Store(
            id="retained-graph-selections",
            data=[],
            storage_type="memory",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Sigma multiplier",
                            htmlFor="sigma-multiplier",
                            style={"fontWeight": "600"},
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "i",
                                    **_ARIA_HIDDEN,
                                    style={
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "19px",
                                        "height": "19px",
                                        "borderRadius": "50%",
                                        "backgroundColor": "#925900",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "flexShrink": "0",
                                    },
                                ),
                                html.Span("Sigma bands do not establish result validity."),
                                html.Details(
                                    [
                                        html.Summary(
                                            "Why?",
                                            style={
                                                "cursor": "pointer",
                                                "fontWeight": "600",
                                                "padding": "2px 0",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Strong("Understanding sigma bands"),
                                                html.P(
                                                    "The shaded region represents measured voltage +/- "
                                                    "(sigma multiplier * measurement sigma)."
                                                ),
                                                html.P(
                                                    "A calculated value inside the band does not "
                                                    "automatically establish that the state-estimation "
                                                    "result is valid.",
                                                    style={"marginBottom": 0},
                                                ),
                                            ],
                                            style={
                                                "position": "absolute",
                                                "zIndex": 10,
                                                "right": 0,
                                                "top": "calc(100% + 6px)",
                                                "width": "min(360px, 80vw)",
                                                "padding": "14px",
                                                "backgroundColor": "#fffaf0",
                                                "border": "1px solid #d5aa57",
                                                "borderRadius": "8px",
                                                "boxShadow": "0 6px 18px rgba(0,0,0,0.16)",
                                                "fontWeight": "normal",
                                                "lineHeight": "1.5",
                                            },
                                        ),
                                    ],
                                    id="sigma-guidance-details",
                                    open=False,
                                    style={"position": "relative", "flexShrink": "0"},
                                ),
                            ],
                            id="voltage-comparison-uncertainty-note",
                            style={
                                "display": "none",
                                "alignItems": "center",
                                "justifyContent": "flex-end",
                                "columnGap": "16px",
                                "rowGap": "8px",
                                "flexWrap": "wrap",
                                "fontSize": "14px",
                                "color": "#694100",
                            },
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "!",
                                    **_ARIA_HIDDEN,
                                    style={
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "backgroundColor": "#b42318",
                                        "color": "white",
                                        "borderRadius": "50%",
                                        "width": "20px",
                                        "height": "20px",
                                        "lineHeight": "20px",
                                        "fontWeight": "bold",
                                        "flexShrink": "0",
                                    },
                                ),
                                html.Span(
                                    "Enter a finite number greater than or equal to zero.",
                                ),
                            ],
                            id="sigma-multiplier-error",
                            role="alert",
                            style={
                                "display": "none",
                                "alignItems": "center",
                                "justifyContent": "flex-end",
                                "columnGap": "12px",
                                "rowGap": "8px",
                                "flexWrap": "wrap",
                                "fontSize": "14px",
                                "color": "#912018",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "columnGap": "24px",
                        "rowGap": "10px",
                        "flexWrap": "wrap",
                    },
                ),
                html.Div(
                    [
                        dcc.Input(
                            id="sigma-multiplier",
                            type="number",
                            min=0,
                            step=0.5,
                            value=2.0,
                            debounce=True,
                            style={"width": "100px", "padding": "6px 8px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "10px",
                        "flexWrap": "wrap",
                    },
                ),
            ],
            id="sigma-multiplier-controls",
            style={"display": "none", "marginBottom": "12px"},
        ),
        # Keep the legacy graph mounted for its existing callback,
        # but display graphs through the retained collection instead.
        html.Div(
            dcc.Graph(
                id="selection-graph",
                style={"display": "none"},
            ),
            style={"display": "none"},
        ),
        dcc.Interval(
            id="sigma-guidance-timer",
            interval=5000,
            n_intervals=0,
            max_intervals=1,
            disabled=True,
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H5(
                            "Selected graphs",
                            style={
                                "margin": "0",
                                "fontWeight": "600",
                            },
                        ),
                        html.Button(
                            [
                                html.I(
                                    className="fa-solid fa-trash-can",
                                    style={"marginRight": "8px"},
                                    **_ARIA_HIDDEN,
                                ),
                                "Clear all graphs",
                            ],
                            id="clear-retained-graphs",
                            n_clicks=0,
                            className="btn btn-danger",
                            title="Remove all selected graphs",
                            style=GRAPH_ACTION_BUTTON_STYLE,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "gap": "16px",
                        "marginBottom": "16px",
                        "flexWrap": "wrap",
                    },
                ),
                html.Div(
                    id="retained-graphs-container",
                    children=[],
                ),
            ],
            id="retained-graphs-section",
            style={"marginTop": "15px"},
        ),
    ],
    style={"margin": "10px"},
)


@callback(
    Output("sigma-multiplier-error", "style"),
    Output("voltage-comparison-uncertainty-note", "style"),
    Input("selected-selection-cell", "data"),
    Input("sigma-multiplier", "value"),
    Input("selection-graph", "style"),
    Input("sigma-multiplier-controls", "style"),
)
def update_voltage_comparison_guidance(selected_cell, multiplier, graph_style, controls_style):
    """Show validation or uncertainty guidance only for voltage comparisons."""
    hidden = {"display": "none"}
    error_visible = {
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "flex-end",
        "columnGap": "16px",
        "rowGap": "8px",
        "flexWrap": "wrap",
        "fontSize": "16px",
        "color": "#912018",
    }
    note_visible = {
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "flex-end",
        "columnGap": "16px",
        "rowGap": "8px",
        "flexWrap": "wrap",
        "fontSize": "14px",
        "color": "#694100",
    }

    is_voltage_measurement = (
        isinstance(selected_cell, dict)
        and selected_cell.get("group") == "sym_voltage_sensor"
        and selected_cell.get("column") == "u_measured"
    )
    controls_visible = isinstance(controls_style, dict) and controls_style.get("display") != "none"
    if not is_voltage_measurement or not controls_visible:
        return hidden, hidden

    valid_multiplier = isinstance(multiplier, (int, float)) and math.isfinite(multiplier) and multiplier >= 0
    if not valid_multiplier:
        return error_visible, hidden

    graph_visible = isinstance(graph_style, dict) and graph_style.get("display") != "none"
    return hidden, note_visible if graph_visible else hidden


@callback(
    Output("sigma-guidance-timer", "n_intervals"),
    Output("sigma-guidance-timer", "disabled"),
    Input("selected-selection-cell", "data"),
)
def restart_sigma_guidance_timer(selected_cell):
    """Restart the five-second guidance window for a new measurement selection."""
    is_voltage_measurement = (
        isinstance(selected_cell, dict)
        and selected_cell.get("group") == "sym_voltage_sensor"
        and selected_cell.get("column") == "u_measured"
    )
    return 0, not is_voltage_measurement


@callback(
    Output("sigma-guidance-details", "open"),
    Input("selected-selection-cell", "data"),
    Input("sigma-guidance-timer", "n_intervals"),
)
def update_sigma_guidance_expansion(selected_cell, n_intervals):
    """Expand on selection, collapse after five seconds; allow manual reopening."""
    is_voltage_measurement = (
        isinstance(selected_cell, dict)
        and selected_cell.get("group") == "sym_voltage_sensor"
        and selected_cell.get("column") == "u_measured"
    )
    return is_voltage_measurement and n_intervals == 0
