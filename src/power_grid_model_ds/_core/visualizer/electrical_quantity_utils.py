# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Utilities for extracting electrical quantities from batch calculation results."""

from collections.abc import Mapping

import numpy as np
from power_grid_model import ComponentType
from power_grid_model.data_types import DenseBatchArray

BATCH_ARRAY_NDIM = 2


def get_scenario_count(
    output_data: Mapping[ComponentType, DenseBatchArray] | None,
) -> int:
    """Return the number of scenarios in a dense batch output dataset.

    All component arrays must have the same scenario count.
    """
    if not output_data:
        return 0

    scenario_counts = set()

    for component_array in output_data.values():
        if component_array.ndim != BATCH_ARRAY_NDIM:
            raise ValueError("Expected a two-dimensional dense batch output array.")

        scenario_counts.add(component_array.shape[0])

    if len(scenario_counts) != 1:
        raise ValueError("Output component arrays have inconsistent scenario counts.")

    return scenario_counts.pop()


def get_available_node_quantities(
    output_data: Mapping[ComponentType, DenseBatchArray] | None,
) -> set[str]:
    """Return supported node quantities present in the batch output."""
    if not output_data or ComponentType.node not in output_data:
        return set()

    node_output = output_data[ComponentType.node]

    if node_output.ndim != BATCH_ARRAY_NDIM:
        raise ValueError("Expected a two-dimensional dense batch output array.")

    if node_output.shape[0] == 0:
        return set()

    field_names = node_output.dtype.names

    if field_names is None or "id" not in field_names:
        return set()

    supported_quantities = {"u_pu", "u_angle"}

    return supported_quantities.intersection(field_names)


def get_available_scalar_attributes(
    output_data: Mapping[ComponentType, DenseBatchArray] | None,
) -> dict[str, list[str]]:
    """Discover real scalar output fields suitable for a component heatmap.

    Exclude IDs, status flags, complex values, and phase/vector-valued fields.
    The visualizer currently has no phase selector or complex-value policy.
    """
    if not output_data:
        return {}

    available: dict[str, list[str]] = {}
    for component, array in output_data.items():
        if array.shape[0] == 0 or not array.dtype.names or "id" not in array.dtype.names:
            continue
        attributes = [
            field
            for field in array.dtype.names
            if field not in {"id", "energized", "status"}
            and array.dtype.fields[field][0].subdtype is None
            and array.dtype.fields[field][0].kind == "f"
        ]
        if attributes:
            available[component.value] = attributes
    return available


def extract_scenario_values(
    output_data: Mapping[ComponentType, DenseBatchArray] | None,
    component_type: ComponentType,
    attribute: str,
    scenario_index: int,
    phase_index: int | None = None,
) -> dict[int, float]:
    """Extract finite electrical values by component ID for one scenario.

    Missing components, invalid values, and non-finite values are excluded.
    Three-phase attributes require an explicit phase index.

    Raises:
        IndexError: If the scenario or phase index is out of range.
        ValueError: If the dataset structure is invalid or a phase
            selection is incompatible with the requested attribute.
    """
    scenario_count = get_scenario_count(output_data)

    if not 0 <= scenario_index < scenario_count:
        raise IndexError(
            f"Scenario index {scenario_index} is outside the available range of 0 to {scenario_count - 1}."
        )

    if output_data is None or component_type not in output_data:
        return {}

    component_array = output_data[component_type]
    field_names = component_array.dtype.names

    if field_names is None or "id" not in field_names or attribute not in field_names:
        return {}

    scenario_data = component_array[scenario_index]
    ids = scenario_data["id"]
    values = scenario_data[attribute]

    if values.ndim == BATCH_ARRAY_NDIM:
        if phase_index is None:
            raise ValueError(f"Attribute '{attribute}' contains phase values; an explicit phase index is required.")

        if not 0 <= phase_index < values.shape[1]:
            raise IndexError(f"Phase index {phase_index} is out of range.")

        values = values[:, phase_index]

    elif values.ndim == 1:
        if phase_index is not None:
            raise ValueError(f"Attribute '{attribute}' is scalar and does not support phase selection.")

    else:
        raise ValueError(f"Unsupported shape for attribute '{attribute}'.")

    result: dict[int, float] = {}
    seen_ids: set[int] = set()

    for raw_component_id, value in zip(ids, values, strict=True):
        component_id = int(raw_component_id)

        if component_id in seen_ids:
            raise ValueError(f"Duplicate component ID {component_id} in scenario {scenario_index}.")

        seen_ids.add(component_id)

        if not np.isfinite(value):
            continue

        result[component_id] = float(value)

    return result
