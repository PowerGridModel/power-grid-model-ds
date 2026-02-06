# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from power_grid_model_ds._core.model.arrays.pgm_arrays import NodeArray


def layout_with_config(layout_name, source_nodes) -> dict:
    """Get the layout options for the selected layout."""
    if layout_name == "breadthfirst":
        config_dict = {
            "name": layout_name,
            "spacingFactor": 2.5,
        }
        if source_nodes:
            config_dict["roots"] = ", ".join(f'[id = "{node}"]' for node in source_nodes)
        return config_dict
    return {"name": layout_name}


def get_default_graph_layout(nodes: NodeArray) -> str:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return "preset"
    return "breadthfirst"
