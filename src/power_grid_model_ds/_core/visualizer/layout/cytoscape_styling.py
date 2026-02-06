# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Contains selectors for the Cytoscape stylesheet."""

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass

NODE_SIZE = 75
BRANCH_WIDTH = 10

_BRANCH_STYLE = {
    "selector": f".{StyleClass.BRANCH.value}",
    "style": {
        "line-color": CYTO_COLORS[StyleClass.BRANCH],
        "target-arrow-color": CYTO_COLORS[StyleClass.BRANCH],
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "width": BRANCH_WIDTH,
    },
}
_NODE_STYLE = {
    "selector": f".{StyleClass.NODE.value}",
    "style": {
        "label": "data(id)",
        "border-width": 5,
        "border-color": "black",
        "font-size": 25,
        "text-halign": "center",
        "text-valign": "center",
        "background-color": CYTO_COLORS[StyleClass.NODE],
        "text-background-color": CYTO_COLORS[StyleClass.NODE],
        "text-background-opacity": 1,
        "text-background-shape": "round-rectangle",
        "width": 75,
        "height": 75,
    },
}
_NODE_LARGE_ID_STYLE = {
    "selector": f".{StyleClass.LARGE_ID_NODE.value}",
    "style": {"font-size": 15},
}
_SELECTED_NODE_STYLE = {
    "selector": f".{StyleClass.NODE.value}:selected, .{StyleClass.NODE.value}:active",
    "style": {"border-width": 5, "border-color": CYTO_COLORS["selected"]},
}

_SELECTED_BRANCH_STYLE = {
    "selector": f".{StyleClass.BRANCH.value}:selected, .{StyleClass.BRANCH.value}:active",
    "style": {"line-color": CYTO_COLORS["selected"], "target-arrow-color": CYTO_COLORS["selected"], "width": 10},
}


_SUBSTATION_NODE_STYLE = {
    "selector": f".{StyleClass.SUBSTATION_NODE.value}",
    "style": {
        "label": "data(id)",
        "shape": "diamond",
        "background-color": CYTO_COLORS[StyleClass.SUBSTATION_NODE],
        "text-background-color": CYTO_COLORS[StyleClass.SUBSTATION_NODE],
        "width": NODE_SIZE * 1.2,
        "height": NODE_SIZE * 1.2,
        "color": "white",
    },
}
_TRANSFORMER_STYLE = {
    "selector": f".{StyleClass.TRANSFORMER.value}",
    "style": {
        "line-color": CYTO_COLORS[StyleClass.TRANSFORMER],
        "target-arrow-color": CYTO_COLORS[StyleClass.TRANSFORMER],
    },
}
_SELECTED_TRANSFORMER_STYLE = {
    "selector": f".{StyleClass.TRANSFORMER.value}:selected, .{StyleClass.TRANSFORMER.value}:active",
    "style": {
        "line-color": CYTO_COLORS["selected_transformer"],
        "target-arrow-color": CYTO_COLORS["selected_transformer"],
    },
}

_LINK_STYLE = {
    "selector": f".{StyleClass.LINK.value}",
    "style": {"line-color": CYTO_COLORS[StyleClass.LINK], "target-arrow-color": CYTO_COLORS[StyleClass.LINK]},
}

_SELECTED_LINK_STYLE = {
    "selector": f".{StyleClass.LINK.value}:selected, .{StyleClass.LINK.value}:active",
    "style": {"line-color": CYTO_COLORS["selected_link"], "target-arrow-color": CYTO_COLORS["selected_link"]},
}

_GENERIC_BRANCH_STYLE = {
    "selector": f".{StyleClass.GENERIC_BRANCH.value}",
    "style": {
        "line-color": CYTO_COLORS[StyleClass.GENERIC_BRANCH],
        "target-arrow-color": CYTO_COLORS[StyleClass.GENERIC_BRANCH],
    },
}
_SELECTED_GENERIC_BRANCH_STYLE = {
    "selector": f".{StyleClass.GENERIC_BRANCH.value}:selected, .{StyleClass.GENERIC_BRANCH.value}:active",
    "style": {
        "line-color": CYTO_COLORS["selected_generic_branch"],
        "target-arrow-color": CYTO_COLORS["selected_generic_branch"],
    },
}

_ASYM_LINE_STYLE = {
    "selector": f".{StyleClass.ASYM_LINE.value}",
    "style": {"line-color": CYTO_COLORS[StyleClass.ASYM_LINE], "target-arrow-color": CYTO_COLORS[StyleClass.ASYM_LINE]},
}

_SELECTED_ASYM_LINE_STYLE = {
    "selector": f".{StyleClass.ASYM_LINE.value}:selected, .{StyleClass.ASYM_LINE.value}:active",
    "style": {
        "line-color": CYTO_COLORS["selected_asym_line"],
        "target-arrow-color": CYTO_COLORS["selected_asym_line"],
    },
}
_OPEN_BRANCH_STYLE = {
    "selector": f".{StyleClass.OPEN_BRANCH.value}",
    "style": {
        "line-style": "dashed",
        "target-arrow-color": CYTO_COLORS[StyleClass.OPEN_BRANCH],
        "source-arrow-color": CYTO_COLORS[StyleClass.OPEN_BRANCH],
    },
}
_OPEN_FROM_SIDE_BRANCH_STYLE = {
    "selector": f".{StyleClass.OPEN_BRANCH_FROM.value}",
    "style": {
        "source-arrow-shape": "diamond",
        "source-arrow-fill": "hollow",
    },
}
_OPEN_TO_SIDE_BRANCH_STYLE = {
    "selector": f".{StyleClass.OPEN_BRANCH_TO.value}",
    "style": {
        "target-arrow-shape": "diamond",
        "target-arrow-fill": "hollow",
    },
}


DEFAULT_STYLESHEET = [
    _NODE_STYLE,
    _NODE_LARGE_ID_STYLE,
    _SUBSTATION_NODE_STYLE,
    _BRANCH_STYLE,
    _TRANSFORMER_STYLE,
    _LINK_STYLE,
    _SELECTED_NODE_STYLE,
    _SELECTED_BRANCH_STYLE,
    _SELECTED_TRANSFORMER_STYLE,
    _SELECTED_LINK_STYLE,
    _GENERIC_BRANCH_STYLE,
    _SELECTED_GENERIC_BRANCH_STYLE,
    _ASYM_LINE_STYLE,
    _SELECTED_ASYM_LINE_STYLE,
    # Note: Keep the OPEN BRANCH styles last in list, otherwise they potentially get overridden.
    _OPEN_BRANCH_STYLE,
    _OPEN_FROM_SIDE_BRANCH_STYLE,
    _OPEN_TO_SIDE_BRANCH_STYLE,
]
