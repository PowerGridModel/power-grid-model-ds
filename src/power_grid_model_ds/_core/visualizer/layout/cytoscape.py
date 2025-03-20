from typing import Any, Literal

import dash_cytoscape as cyto
from dash import html

from pgm_visualizer._core.layout.colors import BACKGROUND_COLOR
from pgm_visualizer._core.layout.cytoscape_styling import DEFAULT_STYLESHEET

LayoutOptions = Literal["", "random", "circle", "concentric", "grid", "cose", "breadthfirst", "preset"]

_CYTO_INNER_STYLE = {"width": "100%", "height": "100%", "background-color": BACKGROUND_COLOR}
_CYTO_OUTER_STYLE = {"height": "100vh", "border": "thin lightgrey solid", "margin": "0 5px 0 5px"}


def get_cytoscape_html(layout: LayoutOptions, elements: list[dict[str, Any]]) -> html.Div:
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
