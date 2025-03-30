# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html

SELECTION_OUTPUT_HEADER_STYLE = {"margin": "20px 0 10px 0"}
_SELECTION_OUTPUT_STYLE = {"overflowX": "scroll", "textAlign": "center", "margin": "10px"}

SELECTION_OUTPUT_HTML = html.Div(
    dcc.Markdown("Click on a **node** or **edge** to display its attributes.", style=SELECTION_OUTPUT_HEADER_STYLE),
    id="selection-output",
    style=_SELECTION_OUTPUT_STYLE,
)
