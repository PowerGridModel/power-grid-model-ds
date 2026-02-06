# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_ds._core.visualizer.styling_classification import StyleClass

YELLOW = "#facc37"
CYTO_COLORS = {
    StyleClass.BRANCH.value: YELLOW,
    StyleClass.LINK.value: "#008000",
    StyleClass.TRANSFORMER.value: "#4290f5",
    StyleClass.NODE.value: YELLOW,
    StyleClass.GENERIC_BRANCH.value: "#dddddd",
    StyleClass.ASYM_LINE.value: "#2de2ca",
    "selected": "#e28743",
    "selected_transformer": "#0349a3",
    "selected_link": "#004000",
    "selected_generic_branch": "#9e9e9e",
    "selected_asym_line": "#1D9181",
    "substation_node": "purple",
    "open_branch": "#c9c9c9",
    "highlighted": "#a10000",
}
BACKGROUND_COLOR = "#555555"
