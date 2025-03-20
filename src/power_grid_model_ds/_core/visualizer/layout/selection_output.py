from dash import dcc, html

SELECTION_OUTPUT_HEADER_STYLE = {"margin": "20px 0 10px 0"}
_SELECTION_OUTPUT_STYLE = {"overflowX": "scroll", "textAlign": "center", "margin": "0 20px 20px 20px"}

SELECTION_OUTPUT_HTML = html.Div(
    dcc.Markdown("Click on a **node** or **edge** to display its attributes.", style=SELECTION_OUTPUT_HEADER_STYLE),
    id="search-output",
    style=_SELECTION_OUTPUT_STYLE,
)
