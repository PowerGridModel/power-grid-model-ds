import dash_bootstrap_components as dbc
from dash import dcc, html

_FORM_ELEMENT_STYLE = {
    "display": "block",
    "width": "200px",
    # "margin": "0 20px 20px 20px",
    "verticalAlign": "middle",
    "justifyContent": "center",
}


SEARCH_FORM_HTML = html.Div(
    [
        html.Div(
            dcc.RadioItems(["node", "line", "link", "transformer", "branch"], "node", id="search-form-group-input"),
            style=_FORM_ELEMENT_STYLE,
        ),
        html.Div(dcc.Dropdown(["id"], "id", id="search-form-column-input"), style=_FORM_ELEMENT_STYLE),
        html.Div(
            dcc.Input(placeholder="Enter value to mark", id="search-form-value-input"),
            style=_FORM_ELEMENT_STYLE,
        ),
    ]
)

SEARCH_FORM_TOGGLE = html.Div(
    dbc.Button(
        "Search",
        id="collapse-button",
        className="mb-3",
        color="primary",
        n_clicks=0,
    ),
    style={"margin": "20px"},
)

HEADER_HTML = html.Div(
    [
        SEARCH_FORM_TOGGLE,
        dbc.Collapse(
            SEARCH_FORM_HTML,
            id="collapse",
            is_open=False,
        ),
    ]
)
