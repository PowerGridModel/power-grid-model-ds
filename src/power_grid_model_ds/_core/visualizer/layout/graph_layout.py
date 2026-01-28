from enum import Enum

from power_grid_model_ds._core.model.arrays.pgm_arrays import NodeArray
from power_grid_model_ds._core.model.enums.nodes import NodeType


class LayoutOptions(Enum):
    """Cytoscape layout options."""

    RANDOM = "random"
    CIRCLE = "circle"
    CONCENTRIC = "concentric"
    GRID = "grid"
    COSE = "cose"
    BREADTHFIRST = "breadthfirst"
    PRESET = "preset"

    def layout_with_config(self) -> dict:
        """Get the layout options for the selected layout."""
        if self == LayoutOptions.BREADTHFIRST:
            return {"name": self.value, "roots": f"node[node_type = {NodeType.SUBSTATION_NODE.value}]"}
        return {"name": self.value}

    @staticmethod
    def dropdown_layouts() -> list[str]:
        """Get a list of available layout options for the dropdown."""
        return [option.value for option in LayoutOptions if option != LayoutOptions.PRESET]


def get_default_graph_layout(nodes: NodeArray) -> LayoutOptions:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return LayoutOptions.PRESET
    return LayoutOptions.BREADTHFIRST
