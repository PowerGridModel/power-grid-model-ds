# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Visual proof of concept for the two-winding transformer symbol."""

from urllib.parse import quote

import dash_cytoscape as cyto
from dash import Dash, html

BACKGROUND_COLOR = "#18212f"
SYMBOL_COLOR = "#ffffff"
NODE_COLOR = "#64748b"

SYMBOL_WIDTH = 120
SYMBOL_HEIGHT = 60
CIRCLE_RADIUS = 17
LEFT_CIRCLE_X = 48
RIGHT_CIRCLE_X = 72
CIRCLE_Y = SYMBOL_HEIGHT / 2
SYMBOL_STROKE_WIDTH = 3

NODE_SIZE = 55
EDGE_WIDTH = 3
PORT = 8055

# The external connection points coincide with the circles' outer boundaries.
LEFT_CONNECTION_X = LEFT_CIRCLE_X - CIRCLE_RADIUS
RIGHT_CONNECTION_X = RIGHT_CIRCLE_X + CIRCLE_RADIUS
LEFT_ENDPOINT = f"{LEFT_CONNECTION_X - SYMBOL_WIDTH / 2}px 0px"
RIGHT_ENDPOINT = f"{RIGHT_CONNECTION_X - SYMBOL_WIDTH / 2}px 0px"

TRANSFORMER_SVG = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SYMBOL_WIDTH} {SYMBOL_HEIGHT}">'
    f'<g fill="none" stroke="{SYMBOL_COLOR}" stroke-width="{SYMBOL_STROKE_WIDTH}">'
    f'<circle cx="{LEFT_CIRCLE_X}" cy="{CIRCLE_Y}" r="{CIRCLE_RADIUS}"/>'
    f'<circle cx="{RIGHT_CIRCLE_X}" cy="{CIRCLE_Y}" r="{CIRCLE_RADIUS}"/>'
    "</g></svg>"
)

TRANSFORMER_IMAGE = f"data:image/svg+xml,{quote(TRANSFORMER_SVG)}"

ELEMENTS = [
    {"data": {"id": "node-1", "label": "Node 1"}, "position": {"x": 100, "y": 200}},
    {"data": {"id": "node-2", "label": "Node 2"}, "position": {"x": 500, "y": 200}},
    {"data": {"id": "transformer-symbol"}, "position": {"x": 300, "y": 200}, "classes": "transformer-symbol"},
    {"data": {"id": "connection-1", "source": "node-1", "target": "transformer-symbol"}, "classes": "transformer-left"},
    {
        "data": {"id": "connection-2", "source": "transformer-symbol", "target": "node-2"},
        "classes": "transformer-right",
    },
]

_NODE_STYLE = {
    "selector": "node",
    "style": {
        "label": "data(label)",
        "width": NODE_SIZE,
        "height": NODE_SIZE,
        "background-color": NODE_COLOR,
        "color": SYMBOL_COLOR,
    },
}

_EDGE_STYLE = {
    "selector": "edge",
    "style": {"width": EDGE_WIDTH, "line-color": SYMBOL_COLOR, "curve-style": "straight", "target-arrow-shape": "none"},
}

_TRANSFORMER_SYMBOL_STYLE = {
    "selector": ".transformer-symbol",
    "style": {
        "label": "",
        "shape": "rectangle",
        "width": SYMBOL_WIDTH,
        "height": SYMBOL_HEIGHT,
        "background-opacity": 0,
        "background-image": TRANSFORMER_IMAGE,
        "background-fit": "contain",
        "background-clip": "none",
        "background-image-opacity": 1,
        "border-width": 0,
    },
}

_TRANSFORMER_LEFT_STYLE = {
    "selector": ".transformer-left",
    "style": {"target-endpoint": LEFT_ENDPOINT},
}

_TRANSFORMER_RIGHT_STYLE = {
    "selector": ".transformer-right",
    "style": {"source-endpoint": RIGHT_ENDPOINT},
}

STYLESHEET = [_NODE_STYLE, _EDGE_STYLE, _TRANSFORMER_SYMBOL_STYLE, _TRANSFORMER_LEFT_STYLE, _TRANSFORMER_RIGHT_STYLE]

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H3("Two-winding transformer symbol — rendering experiment"),
        cyto.Cytoscape(
            id="transformer-poc",
            elements=ELEMENTS,
            layout={"name": "preset"},
            stylesheet=STYLESHEET,
            style={"width": "100%", "height": "450px", "background-color": BACKGROUND_COLOR},
        ),
    ]
)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
