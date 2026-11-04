# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Resolve coincident electrical node positions for display."""

from collections import defaultdict
from copy import deepcopy
from math import cos, pi, sin

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import NODE_SIZE
from power_grid_model_ds._core.visualizer.typing import VizToComponentElements

MIN_OVERLAPPING_NODES = 2
NODE_GAP = 25.0


def separate_coincident_nodes(
    elements: VizToComponentElements,
    node_scale: float = 1.0,
) -> VizToComponentElements:
    """Separate coincident nodes without changing electrical connectivity.

    Positions are calculated from the supplied elements. Callers should pass
    original parsed elements rather than previously adjusted display elements.
    """
    result = deepcopy(elements)
    groups: dict[tuple[float, float], list[str]] = defaultdict(list)

    for element_id, element in result.items():
        if element.get("data", {}).get("group") != "node":
            continue

        position = element.get("position")
        if position is None:
            continue

        groups[(position["x"], position["y"])].append(element_id)

    separation = NODE_SIZE * node_scale + NODE_GAP

    for (x, y), node_ids in groups.items():
        if len(node_ids) < MIN_OVERLAPPING_NODES:
            continue

        node_ids.sort()
        count = len(node_ids)

        if count == MIN_OVERLAPPING_NODES:
            offsets = [
                (-separation / 2, 0.0),
                (separation / 2, 0.0),
            ]
        else:
            radius = max(
                separation,
                separation * count / (2 * pi),
            )
            offsets = [
                (
                    radius * cos(2 * pi * index / count),
                    radius * sin(2 * pi * index / count),
                )
                for index in range(count)
            ]

        for node_id, (dx, dy) in zip(node_ids, offsets, strict=True):
            result[node_id]["position"] = {
                "x": x + dx,
                "y": y + dy,
            }

    return result
