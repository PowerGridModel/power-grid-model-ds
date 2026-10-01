# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

_BOOTSTRAP_ARROW_ICON_CLASS = "fas fa-arrow-right-long"
LEGENDA_ELEMENTS = [
    html.I(className="fas fa-circle pgm-legend-icon pgm-node-color", id="node-icon"),
    dbc.Tooltip("Node", target="node-icon", placement="bottom"),
    html.I(className="fas fa-diamond pgm-legend-icon pgm-substation-color", id="substation-icon"),
    dbc.Tooltip("Substation", target="substation-icon", placement="bottom"),
    html.I(className=f"{_BOOTSTRAP_ARROW_ICON_CLASS} pgm-legend-icon pgm-node-color", id="line-icon"),
    dbc.Tooltip("Line", target="line-icon", placement="bottom"),
    html.I(className=f"{_BOOTSTRAP_ARROW_ICON_CLASS} pgm-legend-icon pgm-transformer-color", id="transformer-icon"),
    dbc.Tooltip("Transformer", target="transformer-icon", placement="bottom"),
    html.I(className=f"{_BOOTSTRAP_ARROW_ICON_CLASS} pgm-legend-icon pgm-link-color", id="link-icon"),
    dbc.Tooltip("Link", target="link-icon", placement="bottom"),
    html.I(
        className=f"{_BOOTSTRAP_ARROW_ICON_CLASS} pgm-legend-icon pgm-generic-branch-color",
        id="generic-branch-icon",
    ),
    dbc.Tooltip("Generic Branch", target="generic-branch-icon", placement="bottom"),
    html.I(className=f"{_BOOTSTRAP_ARROW_ICON_CLASS} pgm-legend-icon pgm-asym-line-color", id="asym-line-icon"),
    dbc.Tooltip("Asymmetrical Line", target="asym-line-icon", placement="bottom"),
    html.I(className="fas fa-ellipsis pgm-legend-icon pgm-open-branch-color", id="open-branch-icon"),
    dbc.Tooltip("Open Branch", target="open-branch-icon", placement="bottom"),
]
