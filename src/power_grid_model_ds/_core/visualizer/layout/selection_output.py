# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html

SELECTION_OUTPUT_HTML = html.Div(
    dcc.Markdown(
        "Click on a **node** or **edge** to display all its associated components and their attributes."
        "\nYou can also use Ctrl+Click (or Cmd+Click on Mac) to select multiple nodes or edges.",
        className="pgm-selection-header",
    ),
    id="selection-output",
    className="pgm-selection-output",
)

SELECTION_GRAPH_HTML = html.Div(
    dcc.Graph(id="selection-graph", className="pgm-selection-graph-hidden"),
    className="pgm-selection-graph-container",
)
