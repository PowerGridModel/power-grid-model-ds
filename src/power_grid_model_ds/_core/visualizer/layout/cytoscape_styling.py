# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Contains selectors for the Cytoscape stylesheet."""

from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass

NODE_SIZE = 75
BRANCH_WIDTH = 10

_BRANCH_STYLE = {
    "selector": f".{StyleClass.BRANCH.value}",
    "style": {
        "line-color": CYTO_COLORS[ComponentType.line],
        "target-arrow-color": CYTO_COLORS[ComponentType.line],
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
        "background-color": CYTO_COLORS["node"],
        "text-background-color": CYTO_COLORS["node"],
        "text-background-opacity": 1,
        "text-background-shape": "round-rectangle",
        "width": NODE_SIZE,
        "height": NODE_SIZE,
    },
}
_NODE_LARGE_ID_STYLE = {
    "selector": f".{StyleClass.LARGE_ID_NODE.value}",
    "style": {"font-size": 15},
}
_SELECTED_NODE_STYLE = {
    "selector": "node:selected, node:active",
    "style": {"border-width": 5, "border-color": CYTO_COLORS["selected"]},
}

_APPLIANCE_GHOST_NODE_STYLE = {
    "selector": f".{StyleClass.APPLIANCE_GHOST_NODE.value}",
    "style": {
        "label": "",
        "border-width": 5,
        "border-color": "black",
        "font-size": 25,
        "text-halign": "center",
        "text-valign": "center",
        "background-color": CYTO_COLORS["node"],
        "text-background-color": CYTO_COLORS["node"],
        "text-background-opacity": 1,
        "text-background-shape": "round-rectangle",
        "width": NODE_SIZE * 0.25,
        "height": NODE_SIZE * 0.25,
    },
}


_GENERATING_EDGE_STYLE = {
    "selector": f".{StyleClass.GENERATING_APPLIANCE.value}",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "curve-style": "bezier",
        "source-arrow-color": CYTO_COLORS["line"],
        "source-arrow-shape": "vee",
        "arrow-scale": 3.0,
        "width": BRANCH_WIDTH * 0.5,
    },
}
_SOURCE_EDGE_STYLE = {
    "selector": f".{StyleClass.SOURCE.value}",
    "style": {
        "line-color": CYTO_COLORS["substation_node"],
        "source-arrow-color": CYTO_COLORS["substation_node"],
    },
}
_LOADING_EDGE_STYLE = {
    "selector": f".{StyleClass.LOADING_APPLIANCE.value}",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "curve-style": "bezier",
        "target-arrow-color": CYTO_COLORS["line"],
        "target-arrow-shape": "vee",
        "arrow-scale": 3.0,
        "width": BRANCH_WIDTH * 0.5,
    },
}

_SELECTED_BRANCH_STYLE = {
    "selector": "edge:selected, edge:active",
    "style": {
        "line-color": CYTO_COLORS["selected"],
        "target-arrow-color": CYTO_COLORS["selected"],
        "width": 10,
    },
}


_SUBSTATION_NODE_STYLE = {
    "selector": f".{StyleClass.SUBSTATION_NODE.value}",
    "style": {
        "label": "data(id)",
        "shape": "diamond",
        "background-color": CYTO_COLORS["substation_node"],
        "text-background-color": CYTO_COLORS["substation_node"],
        "width": NODE_SIZE * 1.2,
        "height": NODE_SIZE * 1.2,
        "color": "white",
    },
}
_TRANSFORMER_STYLE = {
    "selector": f".{StyleClass.TRANSFORMER.value}",
    "style": {"line-color": CYTO_COLORS["transformer"], "target-arrow-color": CYTO_COLORS["transformer"]},
}
_SELECTED_TRANSFORMER_STYLE = {
    "selector": (
        f".{StyleClass.TRANSFORMER.value}:selected, "
        f".{StyleClass.TRANSFORMER.value}:active, "
        f".{StyleClass.TRANSFORMER.value}:selected, "
        f".{StyleClass.TRANSFORMER.value}:active"
    ),
    "style": {
        "line-color": CYTO_COLORS["selected_transformer"],
        "target-arrow-color": CYTO_COLORS["selected_transformer"],
    },
}

_LINK_STYLE = {
    "selector": f".{StyleClass.LINK.value}",
    "style": {"line-color": CYTO_COLORS["link"], "target-arrow-color": CYTO_COLORS["link"]},
}

_SELECTED_LINK_STYLE = {
    "selector": f".{StyleClass.LINK.value}:selected, .{StyleClass.LINK.value}:active",
    "style": {"line-color": CYTO_COLORS["selected_link"], "target-arrow-color": CYTO_COLORS["selected_link"]},
}

_GENERIC_BRANCH_STYLE = {
    "selector": f".{StyleClass.GENERIC_BRANCH.value}",
    "style": {"line-color": CYTO_COLORS["generic_branch"], "target-arrow-color": CYTO_COLORS["generic_branch"]},
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
    "style": {"line-color": CYTO_COLORS["asym_line"], "target-arrow-color": CYTO_COLORS["asym_line"]},
}

_SELECTED_ASYM_LINE_STYLE = {
    "selector": f".{StyleClass.ASYM_LINE.value}:selected, .{StyleClass.ASYM_LINE.value}:active",
    "style": {
        "line-color": CYTO_COLORS["selected_asym_line"],
        "target-arrow-color": CYTO_COLORS["selected_asym_line"],
    },
}
_OPEN_BRANCH_STYLE = {
    "selector": (f".{StyleClass.OPEN_BRANCH.value}"),
    "style": {
        "line-style": "dashed",
        "target-arrow-color": CYTO_COLORS["open_branch"],
        "source-arrow-color": CYTO_COLORS["open_branch"],
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
_OPEN_LOADING_EDGE_STYLE = {
    "selector": f".{StyleClass.OPEN_LOADING_APPLIANCE.value}",
    "style": {
        "line-style": "dashed",
        "line-color": CYTO_COLORS["open_branch"],
        "target-arrow-color": CYTO_COLORS["open_branch"],
        "target-arrow-fill": "hollow",
    },
}
_OPEN_GENERATING_EDGE_STYLE = {
    "selector": f".{StyleClass.OPEN_GENERATING_APPLIANCE.value}",
    "style": {
        "line-style": "dashed",
        "line-color": CYTO_COLORS["open_branch"],
        "source-arrow-color": CYTO_COLORS["open_branch"],
        "source-arrow-fill": "hollow",
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
    _APPLIANCE_GHOST_NODE_STYLE,
    _GENERATING_EDGE_STYLE,
    _LOADING_EDGE_STYLE,
    _SOURCE_EDGE_STYLE,
    # Note: Keep the OPEN BRANCH styles last in list, otherwise they potentially get overridden.
    _OPEN_BRANCH_STYLE,
    _OPEN_FROM_SIDE_BRANCH_STYLE,
    _OPEN_TO_SIDE_BRANCH_STYLE,
    _OPEN_LOADING_EDGE_STYLE,
    _OPEN_GENERATING_EDGE_STYLE,
]
