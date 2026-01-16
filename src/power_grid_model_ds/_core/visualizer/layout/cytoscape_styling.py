# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Contains selectors for the Cytoscape stylesheet."""

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR, CYTO_COLORS

NODE_SIZE = 100
BRANCH_WIDTH = 10
APPLIANCE_NODE_SIZE = NODE_SIZE * 0.5
APPLIANCE_EDGE_WIDTH = BRANCH_WIDTH

_BRANCH_STYLE = {
    "selector": "edge",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "target-arrow-color": CYTO_COLORS["line"],
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
        "width": 75,
        "height": 75,
    },
}
_PARENT_NODE_STYLE = {
    "selector": "node[group = 'parent_node']",
    "style": {
        "label": "",
        "border-width": 5,
        "border-color": BACKGROUND_COLOR,
        "font-size": 25,
        "text-halign": "center",
        "text-valign": "center",
        "background-color": BACKGROUND_COLOR,
        "text-background-color": BACKGROUND_COLOR,
        "text-background-opacity": 0,
        "text-background-shape": "round-rectangle",
        # "width": 75,
        # "height": 75,
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

_APPLIANCE_STYLE = {
    "selector": "node[group *= '_ghost_node']",
    "style": {
        "label": "data(label)",
        "border-width": 5,
        "border-color": "black",
        "font-size": 25,
        "text-halign": "center",
        "text-valign": "center",
        "background-color": CYTO_COLORS["node"],
        "text-background-color": CYTO_COLORS["node"],
        "text-background-opacity": 1,
        "text-background-shape": "round-rectangle",
        "width": 10,
        "height": 10,
    },
}

_GEN_EDGE_STYLE = {
    "selector": "edge[group = 'sym_gen_edge']",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "source-arrow-color": CYTO_COLORS["line"],
        "curve-style": "bezier",
        "source-arrow-shape": "triangle",
        "source-arrow-size": 100,
        "width": APPLIANCE_EDGE_WIDTH,
    },
}
_LOAD_EDGE_STYLE = {
    "selector": "edge[group = 'sym_load_edge']",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "target-arrow-color": CYTO_COLORS["line"],
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "width": APPLIANCE_EDGE_WIDTH,
    },
}
_SOURCE_EDGE_STYLE = {
    "selector": "edge[group = 'source_edge']",
    "style": {
        "line-color": CYTO_COLORS["substation_node"],
        "source-arrow-color": CYTO_COLORS["substation_node"],
        "curve-style": "bezier",
        "source-arrow-shape": "triangle",
        "source-arrow-size": 100,
        "width": APPLIANCE_EDGE_WIDTH,
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

_OPEN_BRANCH_STYLE = {
    "selector": "edge[from_status = 0], edge[to_status = 0], edge[status = 0]",
    "style": {
        "line-style": "dashed",
        "line-color": CYTO_COLORS["open_branch"],
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
_OPEN_APPLIANCE_EDGE_STYLE = {
    "selector": "edge[status = 0]",
    "style": {
        "source-arrow-shape": "diamond",
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
    _OPEN_BRANCH_STYLE,
    _OPEN_FROM_SIDE_BRANCH_STYLE,
    _OPEN_TO_SIDE_BRANCH_STYLE,
    _APPLIANCE_STYLE,
    _PARENT_NODE_STYLE,
    _GEN_EDGE_STYLE,
    _LOAD_EDGE_STYLE,
    _SOURCE_EDGE_STYLE,
    _OPEN_APPLIANCE_EDGE_STYLE,
]
