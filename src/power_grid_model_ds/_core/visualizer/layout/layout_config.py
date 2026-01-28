from power_grid_model_ds._core.model.arrays.pgm_arrays import NodeArray
from power_grid_model_ds._core.model.enums.nodes import NodeType


def layout_with_config(layout_name) -> dict:
    """Get the layout options for the selected layout."""
    if layout_name == "breadthfirst":
        return {"name": layout_name, "roots": f"node[node_type = {NodeType.SUBSTATION_NODE.value}]"}
    return {"name": layout_name}


def get_default_graph_layout(nodes: NodeArray) -> str:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return "preset"
    return "breadthfirst"
