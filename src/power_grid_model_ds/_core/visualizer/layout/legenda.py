from dash import html

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS

_TEST_SHADOW = "0 0 5px #000"

_NODE_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["node"], "text-shadow": _TEST_SHADOW}
_SUBSTATION_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["substation_node"], "text-shadow": _TEST_SHADOW}
_LINE_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["line"], "text-shadow": _TEST_SHADOW}
_LINK_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["link"], "text-shadow": _TEST_SHADOW}
_TRANSFORMER_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["transformer"], "text-shadow": _TEST_SHADOW}
_OPEN_BRANCH_ICON_STYLE = {"font-size": "2.5em", "margin": "0 10px", "color": CYTO_COLORS["open_branch"], "text-shadow": _TEST_SHADOW}
LEGENDA_HTML = html.Div(
            [
                html.I(className="fas fa-circle", style=_NODE_ICON_STYLE),
                html.I(className="fas fa-diamond", style=_SUBSTATION_ICON_STYLE),
                html.I(className="fas fa-arrow-right-long", style=_LINE_ICON_STYLE),
                html.I(className="fas fa-arrow-right-long", style=_LINK_ICON_STYLE),
                html.I(className="fas fa-arrow-right-long", style=_TRANSFORMER_ICON_STYLE),
                html.I(className="fas fas fa-ellipsis", style=_OPEN_BRANCH_ICON_STYLE),
            ],
)


# <i class="fas fa-ellipsis"></i>