# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Map electrical quantity results to Cytoscape element data."""

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass

MISSING_COLOR = "#9CA3AF"
# Continuous rainbow-style scale: purple -> blue -> cyan -> green -> yellow -> orange -> red.
# The highest relative value is always red. Colours are interpolated between anchors.
RAINBOW_STOPS = (
    (106, 13, 173),
    (59, 40, 204),
    (24, 91, 219),
    (0, 170, 232),
    (0, 206, 181),
    (45, 190, 85),
    (162, 218, 35),
    (255, 230, 0),
    (255, 147, 0),
    (220, 38, 38),
)


# Preserve public colour endpoints used by the legend and existing callers.
LOW_COLOR = RAINBOW_STOPS[0]
HIGH_COLOR = RAINBOW_STOPS[-1]


def _interpolate_color(value: float, minimum: float, maximum: float) -> str:
    """Interpolate between two colours over the selected value range."""
    fraction = 0.5 if minimum == maximum else (value - minimum) / (maximum - minimum)
    fraction = max(0.0, min(1.0, fraction))

    position = fraction * (len(RAINBOW_STOPS) - 1)
    lower_index = min(int(position), len(RAINBOW_STOPS) - 2)
    local_fraction = position - lower_index
    low = RAINBOW_STOPS[lower_index]
    high = RAINBOW_STOPS[lower_index + 1]
    channels = [round(a + (b - a) * local_fraction) for a, b in zip(low, high, strict=True)]
    return f"#{channels[0]:02X}{channels[1]:02X}{channels[2]:02X}"


def apply_electrical_colors(
    elements: Sequence[dict[str, Any]],
    component_group: str,
    values: Mapping[int, float],
) -> tuple[list[dict[str, Any]], dict[str, float | int | None]]:
    """Add electrical display data to matching Cytoscape elements.

    The original elements are not modified. Missing results receive a
    neutral colour. Unrelated elements retain their existing data.
    """
    updated_elements = deepcopy(list(elements))

    matched_values: list[float] = []

    for element in updated_elements:
        data = element.get("data", {})

        if data.get("group") != component_group:
            continue

        associated_ids = data.get("associated_ids", {}).get(component_group, [])

        for component_id in associated_ids:
            if component_id in values:
                matched_values.append(values[component_id])
                break

    minimum = min(matched_values) if matched_values else None
    maximum = max(matched_values) if matched_values else None
    missing_count = 0

    for element in updated_elements:
        data = element.get("data", {})

        # Remove any quantity display data from a previous selection.
        data.pop("electrical_value", None)
        data.pop("electrical_color", None)

        if data.get("group") != component_group:
            continue

        associated_ids = data.get("associated_ids", {}).get(component_group, [])
        matching_values = [values[component_id] for component_id in associated_ids if component_id in values]

        if not matching_values:
            data["electrical_color"] = MISSING_COLOR
            missing_count += 1
            continue

        if len(matching_values) != 1:
            raise ValueError("A visual element maps to multiple electrical values.")

        value = matching_values[0]
        data["electrical_value"] = value
        data["electrical_color"] = _interpolate_color(value, minimum, maximum)

    return updated_elements, {
        "minimum": minimum,
        "maximum": maximum,
        "missing_count": missing_count,
    }


def clear_electrical_colors(
    elements: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Restore default node colours without modifying the original elements."""
    updated_elements = deepcopy(list(elements))

    for element in updated_elements:
        data = element.get("data", {})

        data.pop("electrical_value", None)
        data.pop("electrical_color", None)

        classes = set(element.get("classes", "").split())

        if StyleClass.NODE.value not in classes:
            continue

        if StyleClass.SUBSTATION_NODE.value in classes:
            data["electrical_color"] = CYTO_COLORS["substation_node"]
        else:
            data["electrical_color"] = CYTO_COLORS[StyleClass.NODE.value]

    return updated_elements
