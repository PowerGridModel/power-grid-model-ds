# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from power_grid_model_ds.arrays import NodeArray
from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions


def layout_with_config(layout: LayoutOptions, source_nodes: list[int]) -> dict:
    """Get the layout options for the selected layout."""
    if layout is LayoutOptions.BREADTHFIRST:
        config_dict = {
            "name": layout.value,
            "spacingFactor": 2.5,
        }
        if source_nodes:
            config_dict["roots"] = ", ".join(f'[id = "{node}"]' for node in source_nodes)
        return config_dict
    return {"name": layout.value}


def get_default_graph_layout(nodes: NodeArray) -> LayoutOptions:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return LayoutOptions.PRESET
    return LayoutOptions.BREADTHFIRST
