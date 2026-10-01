# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import dash_cytoscape as cyto
from dash import html

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions
from power_grid_model_ds._core.visualizer.layout.layout_config import layout_with_config


def get_cytoscape_html(layout: LayoutOptions, elements: list[dict[str, Any]], source_available: bool) -> html.Div:
    """Get the Cytoscape HTML element"""
    return html.Div(
        cyto.Cytoscape(
            id="cytoscape-graph",
            layout=layout_with_config(layout, source_available=source_available),
            className="pgm-cytoscape",
            elements=elements,
            stylesheet=DEFAULT_STYLESHEET,
            zoom=1.0,  # Default zoom level
            minZoom=0.05,
            maxZoom=3.0,
            boxSelectionEnabled=True,
            wheelSensitivity=0.2,  # Smooth zooming
        ),
        className="pgm-cytoscape-container",
    )
