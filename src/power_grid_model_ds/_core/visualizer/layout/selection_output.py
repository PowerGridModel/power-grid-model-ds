# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Selected component tables, graph, and sigma-multiplier guidance."""

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

SELECTION_OUTPUT_HEADER_STYLE = {"margin": "20px 0 10px 0"}

_SELECTION_OUTPUT_STYLE = {
    "overflowX": "scroll",
    "textAlign": "center",
    "margin": "10px",
}

_HIDDEN_STYLE = {"display": "none"}

_NOTE_VISIBLE_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "gap": "8px",
    "fontSize": "14px",
    "fontWeight": "400",
    "lineHeight": "20px",
    "color": "#694100",
    "whiteSpace": "nowrap",
}

_NOTE_ICON_STYLE = {
    "display": "inline-flex",
    "alignItems": "center",
    "justifyContent": "center",
    "fontSize": "19px",
    "lineHeight": "20px",
    "color": "#925900",
    "marginRight": "3px",
    "flexShrink": "0",
}

_SIGMA_WARNING_TEXT_STYLE = {
    "color": "#694100",
    "fontSize": "14px",
    "fontWeight": "400",
    "lineHeight": "20px",
}

_ERROR_ICON_STYLE = {
    **_NOTE_ICON_STYLE,
    "color": "#b42318",
    "marginRight": "0",
}

_CONTROLS_HEADER_STYLE = {
    "display": "flex",
    "alignItems": "flex-start",
    "justifyContent": "space-between",
    "columnGap": "24px",
    "rowGap": "10px",
    "flexWrap": "wrap",
}

_CONTROLS_STYLE = {
    "display": "none",
    "marginBottom": "12px",
}

_MULTIPLIER_INPUT_STYLE = {
    "width": "100px",
    "padding": "6px 8px",
}

_SIGMA_LABEL_STYLE = {
    "fontWeight": "600",
    "marginBottom": "0",
}

_SIGMA_FEEDBACK_CONTAINER_STYLE = {
    "marginLeft": "auto",
    "minWidth": "0",
}

_SIGMA_DISCLOSURE_BUTTON_STYLE = {
    "display": "inline-flex",
    "alignItems": "center",
    "justifyContent": "center",
    "gap": "6px",
    "padding": "0",
    "margin": "0",
    "border": "0",
    "background": "transparent",
    "color": "#694100",
    "fontSize": "14px",
    "fontWeight": "400",
    "lineHeight": "20px",
    "whiteSpace": "nowrap",
    "textTransform": "none",
}

_SIGMA_DISCLOSURE_ICON_STYLE = {
    "display": "inline-flex",
    "alignItems": "center",
    "justifyContent": "center",
    "fontSize": "14px",
    "lineHeight": "1",
    "flexShrink": "0",
}

_SIGMA_POPOVER_STYLE = {
    "width": "245px",
    "maxWidth": "80vw",
    "padding": "10px",
    "backgroundColor": "#fffaf0",
    "border": "1px solid #d5aa57",
    "borderRadius": "8px",
    "boxShadow": "0 6px 18px rgba(0,0,0,0.16)",
    "color": "#694100",
    "fontSize": "12px",
    "lineHeight": "1.35",
    "whiteSpace": "normal",
    "zIndex": 1100,
}

_SIGMA_POPOVER_FIRST_PARAGRAPH_STYLE = {
    "marginTop": "4px",
    "marginBottom": "10px",
}

_SIGMA_POPOVER_LAST_PARAGRAPH_STYLE = {
    "marginBottom": 0,
}

_SIGMA_ERROR_HIDDEN_STYLE = {
    "display": "none",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "gap": "5px",
    "fontSize": "14px",
    "fontWeight": "400",
    "lineHeight": "20px",
    "color": "#b42318",
}

_SELECTION_GRAPH_CONTAINER_STYLE = {
    "margin": "10px",
}


SELECTION_OUTPUT_HTML = html.Div(
    dcc.Markdown(
        "Click on a **node** or **edge** to display all its "
        "associated components and their attributes."
        "\nYou can also use Ctrl+Click (or Cmd+Click on Mac) "
        "to select multiple nodes or edges.",
        style=SELECTION_OUTPUT_HEADER_STYLE,
    ),
    id="selection-output",
    style=_SELECTION_OUTPUT_STYLE,
)


_SIGMA_GUIDANCE = html.Div(
    [
        html.I(
            className="bi bi-info-circle-fill",
            style=_NOTE_ICON_STYLE,
            **{"aria-hidden": "true"},
        ),
        html.Span(
            "Sigma bands do not establish result validity.",
            style=_SIGMA_WARNING_TEXT_STYLE,
        ),
        dbc.Button(
            [
                html.I(
                    id="sigma-guidance-caret",
                    className="bi bi-caret-right-fill",
                    style=_SIGMA_DISCLOSURE_ICON_STYLE,
                    **{"aria-hidden": "true"},
                ),
                html.Span("Why?"),
            ],
            id="sigma-guidance-toggle",
            color="link",
            size="sm",
            className="text-decoration-none",
            style=_SIGMA_DISCLOSURE_BUTTON_STYLE,
        ),
        dbc.Popover(
            [
                html.Strong("Understanding sigma bands"),
                html.P(
                    "The shaded region represents measured voltage +/- (sigma multiplier * measurement sigma).",
                    style=_SIGMA_POPOVER_FIRST_PARAGRAPH_STYLE,
                ),
                html.P(
                    "A calculated value inside the band does not "
                    "automatically establish that the state-estimation "
                    "result is valid.",
                    style=_SIGMA_POPOVER_LAST_PARAGRAPH_STYLE,
                ),
            ],
            id="sigma-guidance-popover",
            target="sigma-guidance-toggle",
            is_open=False,
            trigger="legacy",
            placement="bottom-end",
            style=_SIGMA_POPOVER_STYLE,
        ),
    ],
    id="sigma-multiplier-guidance",
    style=_NOTE_VISIBLE_STYLE,
)


_SIGMA_ERROR = html.Div(
    [
        html.I(
            className="bi bi-exclamation-circle-fill",
            style=_ERROR_ICON_STYLE,
            **{"aria-hidden": "true"},
        ),
        html.Span(
            id="sigma-multiplier-error-text",
        ),
    ],
    id="sigma-multiplier-error",
    role="alert",
    style=_SIGMA_ERROR_HIDDEN_STYLE,
)


_SIGMA_MULTIPLIER_CONTROL = html.Div(
    [
        html.Div(
            [
                dbc.Label(
                    "Sigma multiplier",
                    html_for="sigma-multiplier-input",
                    style=_SIGMA_LABEL_STYLE,
                ),
                html.Div(
                    [
                        _SIGMA_GUIDANCE,
                        _SIGMA_ERROR,
                    ],
                    style=_SIGMA_FEEDBACK_CONTAINER_STYLE,
                ),
            ],
            style=_CONTROLS_HEADER_STYLE,
        ),
        dbc.Input(
            id="sigma-multiplier-input",
            type="number",
            value=3,
            min=0,
            step=0.1,
            style=_MULTIPLIER_INPUT_STYLE,
        ),
    ],
    id="sigma-multiplier-control",
    style=_CONTROLS_STYLE,
)


SELECTION_GRAPH_HTML = html.Div(
    [
        dcc.Store(
            id="selected-selection-cell",
            storage_type="memory",
        ),
        _SIGMA_MULTIPLIER_CONTROL,
        dcc.Graph(
            id="selection-graph",
            style=_HIDDEN_STYLE,
        ),
    ],
    style=_SELECTION_GRAPH_CONTAINER_STYLE,
)


@callback(
    Output("sigma-guidance-caret", "className"),
    Input("sigma-guidance-popover", "is_open"),
)
def update_sigma_guidance_caret(is_open):
    """Keep the disclosure icon consistent with the popover state."""
    if is_open:
        return "bi bi-caret-down-fill"
    return "bi bi-caret-right-fill"
