import dash_bootstrap_components as dbc
from dash import html

# Create your form components
group_input = dbc.Select(
    id="search-form-group-input",
    options=[
        {"label": "node", "value": "node"},
        {"label": "line", "value": "line"},
        {"label": "link", "value": "link"},
        {"label": "transformer", "value": "transformer"},
        {"label": "branch", "value": "branch"},
    ],
    value="node",  # Default value
    style={"width": "150px", "display": "inline-block"}
)

column_input = dbc.Select(
    id="search-form-column-input",
    options=[{"label": "id", "value": "id"}],
    value="id",  # Default value
    style={"width": "150px", "display": "inline-block"}
)

value_input = dbc.Input(
    id="search-form-value-input",
    placeholder="Enter value",
    type="text",
    style={"width": "150px", "display": "inline-block"}
)

# Arrange as a sentence
SEARCH_FORM_HTML = html.Div(
    [
        html.Span("Search ", className="mr-2", style={"margin-right": "8px"}),
        group_input,
        html.Span(" with ", className="mx-2", style={"margin": "0 8px"}),
        column_input,
        html.Span(" == ", className="mx-2", style={"margin": "0 8px"}),
        value_input,
    ],
style={
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",  # Centers items horizontally
        "padding": "10px",
        "margin": "0 auto",  # Centers the container itself
        "width": "100%"  # Ensures the container takes full width
    }
)
