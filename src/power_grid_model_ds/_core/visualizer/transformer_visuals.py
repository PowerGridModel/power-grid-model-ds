# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Add presentation-only symbols for positioned two-winding transformers."""

from copy import deepcopy
from math import atan2, degrees, hypot
from typing import Any

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass
from power_grid_model_ds._core.visualizer.transformer_constants import (
    MIN_TRANSFORMER_CONNECTION_LENGTH,
    TRANSFORMER_CONNECTION_CLASS,
    TRANSFORMER_FROM_SUFFIX,
    TRANSFORMER_GROUP,
    TRANSFORMER_OPEN_CLASS,
    TRANSFORMER_OPEN_FROM_CLASS,
    TRANSFORMER_OPEN_TO_CLASS,
    TRANSFORMER_SYMBOL_CLASS,
    TRANSFORMER_SYMBOL_GROUP,
    TRANSFORMER_SYMBOL_SUFFIX,
    TRANSFORMER_TO_SUFFIX,
    TRANSFORMER_VISUAL_PREFIX,
    VISUAL_ONLY_KEY,
)


def add_transformer_visuals(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep original electrical edges and add symbols for positioned endpoints."""
    result = deepcopy(elements)
    nodes = {
        str(item["data"]["id"]): item
        for item in elements
        if "source" not in item["data"] and "target" not in item["data"]
    }
    existing_ids = {str(item["data"]["id"]) for item in elements}

    for item in elements:
        data = item["data"]
        if data.get("group") != TRANSFORMER_GROUP or "source" not in data or "target" not in data:
            continue
        source = nodes.get(str(data["source"]))
        target = nodes.get(str(data["target"]))
        if not source or not target or "position" not in source or "position" not in target:
            continue
        a, b = source["position"], target["position"]
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]
        if hypot(dx, dy) <= MIN_TRANSFORMER_CONNECTION_LENGTH:
            continue

        transformer_id = str(data["id"])
        prefix = f"{TRANSFORMER_VISUAL_PREFIX}{transformer_id}"
        symbol_id = f"{prefix}{TRANSFORMER_SYMBOL_SUFFIX}"
        from_id = f"{prefix}{TRANSFORMER_FROM_SUFFIX}"
        to_id = f"{prefix}{TRANSFORMER_TO_SUFFIX}"
        new_ids = {symbol_id, from_id, to_id}
        if existing_ids & new_ids:
            raise ValueError(f"Visual element ID collision for transformer {transformer_id}")
        existing_ids.update(new_ids)

        midpoint = {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}
        angle = degrees(atan2(dy, dx))
        classes = set(item.get("classes", "").split())
        from_classes = [TRANSFORMER_CONNECTION_CLASS]
        to_classes = [TRANSFORMER_CONNECTION_CLASS]
        # The original OPEN_BRANCH classification dashes the entire transformer
        # edge if either terminal is open. Preserve it on both visual segments.
        if StyleClass.OPEN_BRANCH.value in classes:
            from_classes.append(TRANSFORMER_OPEN_CLASS)
            to_classes.append(TRANSFORMER_OPEN_CLASS)
        if StyleClass.OPEN_BRANCH_FROM.value in classes:
            from_classes.append(TRANSFORMER_OPEN_FROM_CLASS)
        if StyleClass.OPEN_BRANCH_TO.value in classes:
            to_classes.append(TRANSFORMER_OPEN_TO_CLASS)

        result.extend(
            [
                {
                    "data": {
                        "id": symbol_id,
                        "group": TRANSFORMER_SYMBOL_GROUP,
                        "component_id": transformer_id,
                        "symbol_angle": angle,
                        "symbol_color": CYTO_COLORS[StyleClass.TRANSFORMER],
                        "symbol_selected_color": CYTO_COLORS["selected_transformer"],
                        "associated_ids": deepcopy(data.get("associated_ids", {})),
                        VISUAL_ONLY_KEY: True,
                    },
                    "position": midpoint,
                    "classes": TRANSFORMER_SYMBOL_CLASS,
                    "grabbable": True,
                    "selectable": True,
                },
                {
                    "data": {
                        "id": from_id,
                        "source": data["source"],
                        "target": symbol_id,
                        "associated_ids": {},
                        VISUAL_ONLY_KEY: True,
                    },
                    "classes": " ".join(from_classes),
                    "selectable": False,
                },
                {
                    "data": {
                        "id": to_id,
                        "source": symbol_id,
                        "target": data["target"],
                        "associated_ids": {},
                        VISUAL_ONLY_KEY: True,
                    },
                    "classes": " ".join(to_classes),
                    "selectable": False,
                },
            ]
        )

    return result
