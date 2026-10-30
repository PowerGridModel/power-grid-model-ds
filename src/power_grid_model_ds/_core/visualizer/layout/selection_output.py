# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html

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
        dcc.Store(id="selected-selection-cell", storage_type="memory"),
        html.Div(
            [
                html.Label(
                    "Sigma multiplier",
                    htmlFor="sigma-multiplier",
                ),
                dcc.Input(
                    id="sigma-multiplier",
                    type="number",
                    min=0,
                    step=0.5,
                    value=2.0,
                    debounce=True,
                    style={"width": "100px", "marginLeft": "10px"},
                ),
            ],
            id="sigma-multiplier-controls",
            style={"display": "none", "marginBottom": "10px"},
        ),
        dcc.Graph(
            id="selection-graph",
            style={"display": "none"},
        ),
    ],
    style={"margin": "10px"},
)
