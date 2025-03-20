"""Contains selectors for the Cytoscape stylesheet."""

from pgm_visualizer._core.layout.colors import CYTO_COLORS

_BRANCH_STYLE = {
    "selector": "edge",
    "style": {
        "line-color": CYTO_COLORS["line"],
        "target-arrow-color": CYTO_COLORS["line"],
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "width": 7,
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
        "width": 100,
        "height": 100,
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

_OPEN_BRANCH_STYLE = {
    "selector": "edge[from_status = 0], edge[to_status = 0]",
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


DEFAULT_STYLESHEET = [
    _NODE_STYLE,
    _NODE_LARGE_ID_STYLE,
    _SUBSTATION_NODE_STYLE,
    _BRANCH_STYLE,
    _TRANSFORMER_STYLE,
    _SELECTED_NODE_STYLE,
    _SELECTED_BRANCH_STYLE,
    _SELECTED_TRANSFORMER_STYLE,
    _OPEN_BRANCH_STYLE,
    _OPEN_FROM_SIDE_BRANCH_STYLE,
    _OPEN_TO_SIDE_BRANCH_STYLE,
]
