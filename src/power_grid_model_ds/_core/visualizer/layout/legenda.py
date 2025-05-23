# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS

_MARGIN = "0 10px"
_FONT_SIZE = "2.5em"

NODE_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["node"]}
_SUBSTATION_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["substation_node"]}
_LINE_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["line"]}
_LINK_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["link"]}
_TRANSFORMER_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["transformer"]}
_OPEN_BRANCH_ICON_STYLE = {"font-size": _FONT_SIZE, "margin": _MARGIN, "color": CYTO_COLORS["open_branch"]}
LEGENDA_HTML = html.Div(
    [
        html.I(className="fas fa-circle", id="node-icon", style=NODE_ICON_STYLE),
        dbc.Tooltip("Node", target="node-icon", placement="bottom"),
        html.I(className="fas fa-diamond", id="substation-icon", style=_SUBSTATION_ICON_STYLE),
        dbc.Tooltip("Substation", target="substation-icon", placement="bottom"),
        html.I(className="fas fa-arrow-right-long", id="line-icon", style=_LINE_ICON_STYLE),
        dbc.Tooltip("Line", target="line-icon", placement="bottom"),
        html.I(className="fas fa-arrow-right-long", id="transformer-icon", style=_TRANSFORMER_ICON_STYLE),
        dbc.Tooltip("Transformer", target="transformer-icon", placement="bottom"),
        html.I(className="fas fa-arrow-right-long", id="link-icon", style=_LINK_ICON_STYLE),
        dbc.Tooltip("Link", target="link-icon", placement="bottom"),
        html.I(className="fas fa-ellipsis", id="open-branch-icon", style=_OPEN_BRANCH_ICON_STYLE),
        dbc.Tooltip("Open Branch", target="open-branch-icon", placement="bottom"),
    ],
    style={
        "display": "flex",
        "align-items": "center",
        "margin": _MARGIN,
        "width": "100%",
        "text-shadow": "0 0 5px #000",
    },
)
