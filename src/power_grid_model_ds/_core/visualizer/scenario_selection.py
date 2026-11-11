# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Scenario selection, optional timestamp validation, and component-state extraction."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import numpy as np
from power_grid_model import ComponentType
from power_grid_model.data_types import BatchDataset
from power_grid_model.utils import get_dataset_batch_size, get_dataset_scenario

BatchData = BatchDataset


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


def get_scenario_count(*datasets: BatchData | None) -> int | None:
    """Return the common scenario count across available batch datasets."""
    counts: list[int] = []
    for dataset in datasets:
        if dataset is None:
            continue
        if not dataset:
            raise ValueError("Cannot determine scenario count from an empty batch dataset")
        counts.append(get_dataset_batch_size(dataset))

    if not counts:
        return None
    if len(set(counts)) != 1:
        raise ValueError("Batch datasets have inconsistent scenario counts")
    return counts[0]


def _get_scenario_count(datasets: tuple[BatchData | None, ...]) -> int:
    """Require at least one batch dataset and return its common scenario count."""
    count = get_scenario_count(*datasets)
    if count is None:
        raise ValueError("Timestamp selection requires batch data")
    return count


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


def _scenario_records(
    dataset: BatchData,
    component_type: ComponentType,
    scenario_index: int,
) -> np.ndarray | Mapping[str, np.ndarray] | None:
    """Extract one scenario without modifying the source batch dataset."""
    count = get_scenario_count(dataset)
    if (
        count is None
        or not isinstance(scenario_index, (int, np.integer))
        or isinstance(scenario_index, (bool, np.bool_))
        or not 0 <= scenario_index < count
    ):
        raise IndexError("Scenario index is outside the available batch range")
    if component_type not in dataset:
        return None
    return get_dataset_scenario(dataset, int(scenario_index))[component_type]


def get_component_state(
    dataset: BatchData,
    component_type: ComponentType,
    component_id: int,
    scenario_index: int,
) -> dict[str, object] | None:
    """Return a component's raw record in one scenario, matched by ID.

    Supports structured and columnar dense/sparse batches. Returned values
    are independent Python scalars or lists, not mutable views of the batch.
    """
    records = _scenario_records(dataset, component_type, scenario_index)
    if records is None:
        return None

    if isinstance(records, Mapping):
        if "id" not in records:
            raise ValueError("Scenario component data has no id attribute")
        ids = np.asarray(records["id"])
        matches = np.flatnonzero(ids == component_id)
        if matches.size == 0:
            return None
        if matches.size > 1:
            raise ValueError(f"Duplicate component ID {component_id} in scenario {scenario_index}")
        index = int(matches[0])
        return {name: np.asarray(values[index]).tolist() for name, values in records.items()}

    if records.dtype.names is None or "id" not in records.dtype.names:
        raise ValueError("Scenario component data must contain an id field")
    matches = np.flatnonzero(records["id"] == component_id)
    if matches.size == 0:
        return None
    if matches.size > 1:
        raise ValueError(f"Duplicate component ID {component_id} in scenario {scenario_index}")
    record = records[int(matches[0])]
    return {name: record[name].tolist() for name in record.dtype.names}


def _present_mask(values: np.ndarray) -> np.ndarray:
    """Identify supplied update elements using PGM-style empty sentinels."""
    kind = values.dtype.kind
    if kind == "f":
        return ~np.isnan(values)
    if kind == "i":
        return values != np.iinfo(values.dtype).min
    if kind == "u":
        return values != np.iinfo(values.dtype).max
    if kind in ("U", "S"):
        return values != ""
    if kind == "b":
        return np.ones(values.shape, dtype=bool)
    raise TypeError(f"Unsupported update attribute dtype: {values.dtype}")


def get_effective_component_state(
    base_state: Mapping[str, Any],
    update_data: BatchData | None,
    component_type: ComponentType,
    component_id: int,
    scenario_index: int,
) -> dict[str, object]:
    """Overlay non-empty scenario updates on a copied base component record.

    Only attributes already present in base_state are merged. Calculation
    outputs are intentionally not part of the effective input state.
    """
    effective = {name: np.asarray(value).tolist() for name, value in base_state.items()}
    if int(effective["id"]) != component_id:
        raise ValueError("Base component ID does not match the requested component ID")
    if update_data is None:
        return effective

    update = get_component_state(update_data, component_type, component_id, scenario_index)
    if update is None:
        return effective
    records = _scenario_records(update_data, component_type, scenario_index)
    if records is None:
        raise ValueError("Scenario update records are unavailable")

    for name, new_value in update.items():
        if name == "id" or name not in effective:
            continue
        if isinstance(records, Mapping):
            field_dtype = np.asarray(records[name]).dtype
        else:
            field_dtype = records.dtype.fields[name][0]
            if field_dtype.subdtype is not None:
                field_dtype = field_dtype.subdtype[0]
        new = np.asarray(new_value, dtype=field_dtype)
        old = np.asarray(effective[name])
        if old.shape != new.shape:
            raise ValueError(f"Shape mismatch for update attribute {name!r}")
        mask = _present_mask(new)
        effective[name] = np.where(mask, new, old).tolist()
    return effective
