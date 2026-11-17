# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import dash_cytoscape as cyto
from dash import html

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions
from power_grid_model_ds._core.visualizer.layout.layout_config import layout_with_config
from power_grid_model_ds._core.visualizer.layout.transformer_rendering import prepare_transformer_rendering

_CYTO_INNER_STYLE = {"width": "100%", "height": "100%", "background-color": BACKGROUND_COLOR}
_CYTO_OUTER_STYLE = {"height": "80vh"}


def get_cytoscape_html(layout: LayoutOptions, elements: list[dict[str, Any]], source_available: bool) -> html.Div:
    """Create the Cytoscape graph, including draggable transformer presentation elements."""
    rendered_elements = prepare_transformer_rendering(elements) if layout is LayoutOptions.PRESET else elements
    return html.Div(
        cyto.Cytoscape(
            id="cytoscape-graph",
            layout=layout_with_config(layout, source_available=source_available),
            style=_CYTO_INNER_STYLE,
            elements=rendered_elements,
            stylesheet=DEFAULT_STYLESHEET,
            zoom=1.0,
            minZoom=0.05,
            maxZoom=3.0,
            boxSelectionEnabled=True,
            responsive=True,
            autoRefreshLayout=True,
            wheelSensitivity=0.2,
        ),
        style=_CYTO_OUTER_STYLE,
    )
