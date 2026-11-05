# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Timestamp mapping and component-state extraction for batch results."""

from collections.abc import Mapping, Sequence
from datetime import datetime

import numpy as np
from power_grid_model import ComponentType
from power_grid_model.data_types import DenseBatchArray

BatchData = Mapping[ComponentType, DenseBatchArray]


BATCH_DIMENSIONS = 2


def _parse_timestamps(timestamps: Sequence[str]) -> tuple[str, ...]:
    """Validate timestamp syntax, timezone information, and uniqueness."""
    if isinstance(timestamps, (str, bytes)):
        raise ValueError("timestamps must be a sequence of timestamp strings")

    values = tuple(timestamps)

    if not values:
        raise ValueError("At least one timestamp is required")

    parsed = []

    for value in values:
        if not isinstance(value, str):
            raise ValueError("Each timestamp must be an ISO 8601 string")

        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"Invalid timestamp: {value!r}") from exc

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Each timestamp must include a timezone offset")

        parsed.append(timestamp)

    if len(set(parsed)) != len(parsed):
        raise ValueError("Found duplicate timestamps")

    return values


def _get_scenario_count(datasets: tuple[BatchData | None, ...]) -> int:
    """Determine the common scenario count across supplied batch datasets."""
    scenario_counts = set()

    for dataset in datasets:
        if dataset is None:
            continue

        for array in dataset.values():
            if array.ndim != BATCH_DIMENSIONS:
                raise ValueError("Timestamp selection requires two-dimensional batch arrays")

            scenario_counts.add(array.shape[0])

    if not scenario_counts:
        raise ValueError("Timestamp selection requires batch data")

    if len(scenario_counts) != 1:
        raise ValueError("Batch datasets have inconsistent scenario counts")

    return scenario_counts.pop()


def validate_timestamps(
    timestamps: Sequence[str],
    *datasets: BatchData | None,
) -> tuple[str, ...]:
    """Validate timezone-aware timestamps against batch scenario counts."""
    values = _parse_timestamps(timestamps)
    scenario_count = _get_scenario_count(datasets)

    if len(values) != scenario_count:
        raise ValueError(f"Expected {scenario_count} timestamps, received {len(values)}")

    return values


def get_component_state(
    dataset: BatchData,
    component_type: ComponentType,
    component_id: int,
    scenario_index: int,
) -> dict[str, object] | None:
    """Return a component's available fields in one batch scenario.

    Component IDs are matched within the selected scenario because component
    ordering may differ between scenarios. Missing components return None.
    """
    if component_type not in dataset:
        return None

    array = dataset[component_type]

    if array.ndim != BATCH_DIMENSIONS:
        raise ValueError("Component-state inspection requires batch data")

    if (
        not isinstance(scenario_index, (int, np.integer))
        or isinstance(scenario_index, (bool, np.bool_))
        or scenario_index < 0
        or scenario_index >= array.shape[0]
    ):
        raise IndexError("Scenario index is outside the available batch range")

    scenario = array[scenario_index]
    matches = np.flatnonzero(scenario["id"] == component_id)

    if matches.size == 0:
        return None

    if matches.size > 1:
        raise ValueError(f"Duplicate component ID {component_id} in scenario {scenario_index}")

    record = scenario[int(matches[0])]

    return {field: record[field].tolist() for field in record.dtype.names or ()}
