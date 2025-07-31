# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

SPAN_TEXT_STYLE = {"color": "white", "margin-right": "8px", "font-weight": "bold", "text-shadow": "0 0 5px #000"}
_INPUT_STYLE = {"width": "150px", "display": "inline-block"}
# Create your form components
GROUP_INPUT = dbc.Select(
    id="search-form-group-input",
    options=[
        {"label": "node", "value": "node"},
        {"label": "line", "value": "line"},
        {"label": "link", "value": "link"},
        {"label": "transformer", "value": "transformer"},
        {"label": "branch", "value": "branch"},
    ],
    value="node",  # Default value
    style=_INPUT_STYLE,
)

COLUMN_INPUT = dbc.Select(
    id="search-form-column-input",
    options=[{"label": "id", "value": "id"}],
    value="id",  # Default value
    style=_INPUT_STYLE,
)

VALUE_INPUT = dbc.Input(id="search-form-value-input", placeholder="Enter value", type="text", style=_INPUT_STYLE)

OPERATOR_INPUT = dbc.Select(
    id="search-form-operator-input",
    options=[
        {"label": "=", "value": "="},
        {"label": "<", "value": "<"},
        {"label": ">", "value": ">"},
        {"label": "!=", "value": "!="},
    ],
    value="=",  # Default value
    style={"width": "60px", "display": "inline-block", "margin": "0 8px"},
)


# Arrange as a sentence
SEARCH_ELEMENTS = [
    html.Div(
        [
            html.Span("Search ", style=SPAN_TEXT_STYLE),
            GROUP_INPUT,
            html.Span(" with ", style=SPAN_TEXT_STYLE),
            COLUMN_INPUT,
            OPERATOR_INPUT,
            VALUE_INPUT,
        ]
    )
]
