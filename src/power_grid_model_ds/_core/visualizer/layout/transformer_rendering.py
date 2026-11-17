# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Reuse Cytoscape's native draggable symbol node and visual edge elements."""

from typing import Any

from power_grid_model_ds._core.visualizer.transformer_constants import TRANSFORMER_HIDDEN_CLASS
from power_grid_model_ds._core.visualizer.transformer_visuals import add_transformer_visuals


def prepare_transformer_rendering(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retain electrical edges for data; expose draggable presentation nodes."""
    result = add_transformer_visuals(elements)
    converted = {item["data"]["component_id"] for item in result if item["data"].get("group") == "transformer_symbol"}
    for item in result:
        data = item["data"]
        if data.get("group") != "transformer" or str(data.get("id")) not in converted:
            continue
        classes = item.get("classes", "").split()
        if TRANSFORMER_HIDDEN_CLASS not in classes:
            classes.append(TRANSFORMER_HIDDEN_CLASS)
        item["classes"] = " ".join(classes)
    return result
