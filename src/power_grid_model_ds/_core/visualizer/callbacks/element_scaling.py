from dash import Input, Output, callback
from copy import deepcopy
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET, BRANCH_WIDTH, NODE_SIZE


@callback(
    Output('cytoscape-graph', 'stylesheet', allow_duplicate=True),
    Input('node-scale-input', 'value'),
    Input('edge-scale-input', 'value'),
    prevent_initial_call=True
)
def scale_elements(node_scale, edge_scale):
    for scale_factor in (node_scale, edge_scale):
        if scale_factor is None or scale_factor <= 0:
            scale_factor = 1

    new_stylesheet = deepcopy(DEFAULT_STYLESHEET)
    edge_style = {
        "selector": "edge",
        "style": {
            "width": BRANCH_WIDTH * edge_scale,
        },
    }
    new_stylesheet.append(edge_style)
    node_style = {
        "selector": "node",
        "style": {
            "height": NODE_SIZE * node_scale,
            "width": NODE_SIZE * node_scale,
        },
    }
    new_stylesheet.append(node_style)
    return new_stylesheet
