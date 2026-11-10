# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Selection tables, graphs, and measurement-comparison guidance."""

import math

from dash import Input, Output, callback, dcc, html

SELECTION_OUTPUT_HEADER_STYLE = {"margin": "20px 0 10px 0"}
_SELECTION_OUTPUT_STYLE = {"overflowX": "scroll", "textAlign": "center", "margin": "10px"}
_HIDDEN_STYLE = {"display": "none"}

_NOTE_VISIBLE_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "gap": "8px",
    "fontSize": "14px",
    "color": "#694100",
}

_NOTE_ICON_STYLE = {
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
}

_ERROR_ICON_STYLE = {
    **_NOTE_ICON_STYLE,
    "backgroundColor": "#b42318",
}

_CONTROLS_HEADER_STYLE = {
    "display": "flex",
    "alignItems": "flex-start",
    "justifyContent": "space-between",
    "columnGap": "24px",
    "rowGap": "10px",
    "flexWrap": "wrap",
}

_CONTROLS_STYLE = {"display": "none", "marginBottom": "12px"}

_MULTIPLIER_INPUT_STYLE = {
    "width": "100px",
    "padding": "6px 8px",
}

_INVALID_MULTIPLIER_INPUT_STYLE = {
    **_MULTIPLIER_INPUT_STYLE,
    "border": "2px solid #b42318",
    "color": "#b42318",
}

_ERROR_VISIBLE_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "gap": "8px",
    "fontSize": "14px",
    "color": "#b42318",
}

_MULTIPLIER_FIELD_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "alignItems": "flex-start",
    "gap": "8px",
}

_CONTROLS_MESSAGE_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "minHeight": "30px",
}

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
        dcc.Store(id="selected-selection-cell"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Sigma multiplier",
                                    htmlFor="sigma-multiplier",
                                    style={"fontWeight": "600"},
                                ),
                                dcc.Input(
                                    id="sigma-multiplier",
                                    type="number",
                                    min=0,
                                    step=0.5,
                                    value=3.0,
                                    debounce=True,
                                    style=_MULTIPLIER_INPUT_STYLE,
                                ),
                            ],
                            style=_MULTIPLIER_FIELD_STYLE,
                        ),
                        html.Div(
                            [
                                html.Span("!", role="presentation", style=_ERROR_ICON_STYLE),
                                html.Span("Enter a finite number greater than or equal to zero."),
                            ],
                            id="sigma-multiplier-error",
                            role="alert",
                            style=_HIDDEN_STYLE,
                        ),
                    ],
                    style=_CONTROLS_HEADER_STYLE,
                ),
            ],
            id="sigma-multiplier-controls",
            style=_CONTROLS_STYLE,
        ),
        # This guidance must not be nested inside the optional sigma controls:
        # a measured-versus-calculated comparison can exist without sigma bands.
        html.Div(
            [
                html.Span("i", role="presentation", style=_NOTE_ICON_STYLE),
                html.Span("Sigma bands do not establish result validity."),
            ],
            id="voltage-comparison-uncertainty-note",
            style=_HIDDEN_STYLE,
        ),
        dcc.Graph(id="selection-graph", style=_HIDDEN_STYLE),
    ],
    style={"margin": "10px"},
)


def _is_measurement_comparison_selection(selected_cell):
    """Recognize the measurement attributes supported by the comparison callback."""
    if not isinstance(selected_cell, dict):
        return False
    group = selected_cell.get("group")
    column = selected_cell.get("column")
    return (group == "sym_voltage_sensor" and column == "u_measured") or (
        group == "sym_power_sensor" and column in ("p_measured", "q_measured")
    )


def _is_valid_multiplier(multiplier):
    """Return whether the multiplier is a finite, non-negative number."""
    return isinstance(multiplier, (int, float)) and math.isfinite(multiplier) and multiplier >= 0


def _is_visible(style):
    """Return whether a component's display style is visible."""
    return isinstance(style, dict) and style.get("display") != "none"


def _has_comparison_traces(figure):
    """Distinguish a comparison figure from the ordinary attribute fallback graph."""
    if not isinstance(figure, dict):
        return False
    traces = figure.get("data")
    if not isinstance(traces, (list, tuple)):
        return False
    names = [trace.get("name", "") for trace in traces if isinstance(trace, dict)]
    return any(name.startswith("Measured ") for name in names) and any(
        name.startswith(("Calculated ", "Estimated ")) for name in names
    )


@callback(
    Output("voltage-comparison-uncertainty-note", "style"),
    Input("selected-selection-cell", "data"),
    Input("selection-graph", "style"),
    Input("sigma-multiplier-controls", "style"),
    Input("sigma-multiplier", "value"),
    Input("selection-graph", "figure"),
)
def update_voltage_comparison_guidance(selected_cell, graph_style, controls_style, multiplier=3.0, figure=None):
    """Show the validity note for an actual, visible measurement comparison."""
    if not _is_measurement_comparison_selection(selected_cell) or not _is_visible(graph_style):
        return _HIDDEN_STYLE
    if not _has_comparison_traces(figure):
        return _HIDDEN_STYLE
    # When bands are present, an invalid multiplier produces an empty graph;
    # the error message, rather than the validity note, should be shown.
    if _is_visible(controls_style) and not _is_valid_multiplier(multiplier):
        return _HIDDEN_STYLE
    return _NOTE_VISIBLE_STYLE


@callback(
    Output("sigma-multiplier-error", "style"),
    Output("sigma-multiplier", "style"),
    Input("selected-selection-cell", "data"),
    Input("sigma-multiplier", "value"),
    Input("sigma-multiplier-controls", "style"),
)
def update_sigma_multiplier_validation(selected_cell, multiplier, controls_style):
    """Highlight invalid multipliers for any supported measurement comparison."""
    if not _is_measurement_comparison_selection(selected_cell) or not _is_visible(controls_style):
        return _HIDDEN_STYLE, _MULTIPLIER_INPUT_STYLE
    if _is_valid_multiplier(multiplier):
        return _HIDDEN_STYLE, _MULTIPLIER_INPUT_STYLE
    return _ERROR_VISIBLE_STYLE, _INVALID_MULTIPLIER_INPUT_STYLE
