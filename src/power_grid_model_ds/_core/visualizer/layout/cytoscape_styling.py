# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Contains selectors for the Cytoscape stylesheet."""

from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS

NODE_SIZE = 75
BRANCH_WIDTH = 10

_BRANCH_STYLE = {
    "selector": "edge",
    "style": {
        "line-color": CYTO_COLORS[ComponentType.line],
        "target-arrow-color": CYTO_COLORS[ComponentType.line],
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "width": BRANCH_WIDTH,
    },
}
_NODE_STYLE = {
    "selector": "node",
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
    "selector": "node[id > 10000000]",
    "style": {"font-size": 15},
}
_SELECTED_NODE_STYLE = {
    "selector": "node:selected, node:active",
    "style": {"border-width": 5, "border-color": CYTO_COLORS["selected"]},
}

_SELECTED_BRANCH_STYLE = {
    "selector": "edge:selected, edge:active",
    "style": {"line-color": CYTO_COLORS["selected"], "target-arrow-color": CYTO_COLORS["selected"], "width": 10},
}


_SUBSTATION_NODE_STYLE = {
    "selector": "node[node_type = 1]",
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
    "selector": "edge[group = 'transformer']",
    "style": {"line-color": CYTO_COLORS["transformer"], "target-arrow-color": CYTO_COLORS["transformer"]},
}
_SELECTED_TRANSFORMER_STYLE = {
    "selector": "edge[group = 'transformer']:selected, edge[group = 'transformer']:active",
    "style": {
        "line-color": CYTO_COLORS["selected_transformer"],
        "target-arrow-color": CYTO_COLORS["selected_transformer"],
    },
}

_LINK_STYLE = {
    "selector": "edge[group = 'link']",
    "style": {"line-color": CYTO_COLORS["link"], "target-arrow-color": CYTO_COLORS["link"]},
}

_SELECTED_LINK_STYLE = {
    "selector": "edge[group = 'link']:selected, edge[group = 'link']:active",
    "style": {"line-color": CYTO_COLORS["selected_link"], "target-arrow-color": CYTO_COLORS["selected_link"]},
}

_GENERIC_BRANCH_STYLE = {
    "selector": "edge[group = 'generic_branch']",
    "style": {"line-color": CYTO_COLORS["generic_branch"], "target-arrow-color": CYTO_COLORS["generic_branch"]},
}
_SELECTED_GENERIC_BRANCH_STYLE = {
    "selector": "edge[group = 'generic_branch']:selected, edge[group = 'generic_branch']:active",
    "style": {
        "line-color": CYTO_COLORS["selected_generic_branch"],
        "target-arrow-color": CYTO_COLORS["selected_generic_branch"],
    },
}

_ASYM_LINE_STYLE = {
    "selector": "edge[group = 'asym_line']",
    "style": {"line-color": CYTO_COLORS["asym_line"], "target-arrow-color": CYTO_COLORS["asym_line"]},
}

_SELECTED_ASYM_LINE_STYLE = {
    "selector": "edge[group = 'asym_line']:selected, edge[group = 'asym_line']:active",
    "style": {
        "line-color": CYTO_COLORS["selected_asym_line"],
        "target-arrow-color": CYTO_COLORS["selected_asym_line"],
    },
}
_OPEN_BRANCH_STYLE = {
    "selector": "edge[from_status = 0], edge[to_status = 0]",
    "style": {
        "line-style": "dashed",
        "target-arrow-color": CYTO_COLORS["open_branch"],
        "source-arrow-color": CYTO_COLORS["open_branch"],
    },
}
_OPEN_FROM_SIDE_BRANCH_STYLE = {
    "selector": "edge[from_status = 0]",
    "style": {
        "source-arrow-shape": "diamond",
        "source-arrow-fill": "hollow",
    },
}
_OPEN_TO_SIDE_BRANCH_STYLE = {
    "selector": "edge[to_status = 0]",
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
