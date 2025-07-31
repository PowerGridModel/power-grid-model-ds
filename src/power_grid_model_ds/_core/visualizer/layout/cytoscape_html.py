# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import dash_cytoscape as cyto
from dash import html

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET

_CYTO_INNER_STYLE = {"width": "100%", "height": "100%", "background-color": BACKGROUND_COLOR}
_CYTO_OUTER_STYLE = {"height": "80vh"}


def get_cytoscape_html(layout: str, elements: list[dict[str, Any]]) -> html.Div:
    """Get the Cytoscape HTML element"""
    return html.Div(
        cyto.Cytoscape(
            id="cytoscape-graph",
            layout={"name": layout},
            style=_CYTO_INNER_STYLE,
            elements=elements,
            stylesheet=DEFAULT_STYLESHEET,
        ),
        style=_CYTO_OUTER_STYLE,
    )
