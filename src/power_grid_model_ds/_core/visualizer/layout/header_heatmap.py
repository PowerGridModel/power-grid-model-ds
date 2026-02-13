# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.callbacks.common import HEADER_HEATMAP_OPTIONS

SPAN_TEXT_STYLE = {"color": "white", "margin-right": "8px", "font-weight": "bold", "text-shadow": "0 0 5px #000"}
_INPUT_STYLE = {"width": "150px", "display": "inline-block"}
# Create your form components
GROUP_INPUT = dbc.Select(
    id="heatmap-group-input",
    options=HEADER_HEATMAP_OPTIONS,
    value="node",  # Default value
    style=_INPUT_STYLE,
)

COLUMN_INPUT = dbc.Select(
    id="heatmap-column-input",
    options=[{"label": "id", "value": "id"}],
    value="id",  # Default value
    style=_INPUT_STYLE,
)

# Arrange as a sentence
HEATMAP_ELEMENTS = [
    html.Div(
        [
            html.Span("Apply heatmap ", style=SPAN_TEXT_STYLE),
            GROUP_INPUT,
            html.Span(" with ", style=SPAN_TEXT_STYLE),
            COLUMN_INPUT,
        ]
    )
]
