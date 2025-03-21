import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR
from power_grid_model_ds._core.visualizer.layout.legenda import LEGENDA_HTML
from power_grid_model_ds._core.visualizer.layout.search_form import SEARCH_FORM_HTML


HEADER_HTML = dbc.Row(
    [
        dbc.Col(LEGENDA_HTML, className="d-flex align-items-center", style={"margin": "0 10px"}),
        dbc.Col(
            dbc.Card(SEARCH_FORM_HTML, style={"background-color": "#555555", "color": "white", "border": "none", "border-radius": 0}),
            className="d-flex justify-content-center align-items-center"
        ),
        dbc.Col(
            # Right column - empty or for future controls
            html.Div(),
            className="d-flex justify-content-end align-items-center"
        ),
    ],
    style={"background-color": BACKGROUND_COLOR},


)