# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

# Create your form components
GROUP_INPUT = dbc.Select(
    id="search-form-group-input",
    options=[
        {"label": "node", "value": "node"},
        {"label": "line", "value": "line"},
        {"label": "link", "value": "link"},
        {"label": "transformer", "value": "transformer"},
        {"label": "branch", "value": "branches"},
    ],
    value="node",  # Default value
    className="pgm-search-input",
)

COLUMN_INPUT = dbc.Select(
    id="search-form-column-input",
    options=[{"label": "id", "value": "id"}],
    value="id",  # Default value
    className="pgm-search-input",
)

VALUE_INPUT = dbc.Input(
    id="search-form-value-input", placeholder="Enter value", type="text", className="pgm-search-input"
)

OPERATOR_INPUT = dbc.Select(
    id="search-form-operator-input",
    options=[
        {"label": "=", "value": "="},
        {"label": "<", "value": "<"},
        {"label": ">", "value": ">"},
        {"label": "!=", "value": "!="},
    ],
    value="=",  # Default value
    className="pgm-search-operator",
)


# Arrange as a sentence
SEARCH_ELEMENTS = [
    html.Div(
        [
            html.Span("Search ", className="pgm-search-label"),
            GROUP_INPUT,
            html.Span(" with ", className="pgm-search-label"),
            COLUMN_INPUT,
            OPERATOR_INPUT,
            VALUE_INPUT,
        ]
    )
]
