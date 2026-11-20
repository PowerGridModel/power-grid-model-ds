# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for F05 scenario selection and component-state preparation."""

import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer.scenario_selection import (
    get_component_state,
    get_effective_component_state,
    get_scenario_count,
    validate_timestamps,
)


def make_output_data():
    """Create three scenarios with different component ordering."""
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (3, 2))
    nodes["id"] = [[10, 20], [20, 10], [10, 20]]
    nodes["u"] = [
        [[101.0, 102.0, 103.0], [201.0, 202.0, 203.0]],
        [[211.0, 212.0, 213.0], [111.0, 112.0, 113.0]],
        [[121.0, 122.0, 123.0], [221.0, 222.0, 223.0]],
    ]
    return {ComponentType.node: nodes}


def make_line_updates():
    lines = initialize_array(DatasetType.update, ComponentType.line, (2, 1))
    lines["id"] = 5
    lines["from_status"][0, 0] = 0
    return {ComponentType.line: lines}


def test_validate_timestamps_accepts_matching_batch_size():
    timestamps = [
        "2026-11-05T09:00:00+01:00",
        "2026-11-05T09:15:00+01:00",
        "2026-11-05T09:30:00+01:00",
    ]
    assert validate_timestamps(timestamps, make_output_data()) == tuple(timestamps)


def test_validate_timestamps_rejects_count_mismatch():
    with pytest.raises(ValueError, match="timestamp"):
        validate_timestamps(["2026-11-05T09:00:00+01:00"], make_output_data())


def test_validate_timestamps_rejects_duplicate_values():
    timestamps = [
        "2026-11-05T09:00:00+01:00",
        "2026-11-05T09:00:00+01:00",
        "2026-11-05T09:30:00+01:00",
    ]
    with pytest.raises(ValueError, match="duplicate"):
        validate_timestamps(timestamps, make_output_data())


def test_component_lookup_uses_id_not_array_position():
    result = get_component_state(make_output_data(), ComponentType.node, 10, 1)
    assert result is not None
    assert np.array_equal(result["u"], [111.0, 112.0, 113.0])


def test_component_lookup_returns_none_for_missing_component():
    assert get_component_state(make_output_data(), ComponentType.node, 999, 1) is None


def test_component_lookup_rejects_invalid_scenario_index():
    with pytest.raises(IndexError):
        get_component_state(make_output_data(), ComponentType.node, 10, 3)


@pytest.mark.parametrize("index", [-1, True, 2, 1.5])
def test_component_lookup_rejects_other_invalid_indices(index):
    with pytest.raises(IndexError):
        get_component_state(make_line_updates(), ComponentType.line, 5, index)


def test_effective_state_applies_explicit_zero():
    base = {"id": 5, "from_status": 1, "to_status": 1}
    result = get_effective_component_state(base, make_line_updates(), ComponentType.line, 5, 0)
    assert result == {"id": 5, "from_status": 0, "to_status": 1}
    assert base == {"id": 5, "from_status": 1, "to_status": 1}


def test_effective_state_preserves_base_for_empty_update():
    base = {"id": 5, "from_status": 1, "to_status": 1}
    result = get_effective_component_state(base, make_line_updates(), ComponentType.line, 5, 1)
    assert result == base


def test_effective_state_does_not_mutate_batch():
    updates = make_line_updates()
    original = updates[ComponentType.line].copy()
    base = {"id": 5, "from_status": 1, "to_status": 1}
    get_effective_component_state(base, updates, ComponentType.line, 5, 0)
    np.testing.assert_array_equal(updates[ComponentType.line], original)


def test_effective_state_supports_partial_three_phase_update():
    base = {"id": 10, "u": [220.0, 221.0, 222.0]}
    data = np.zeros((1, 1), dtype=[("id", "i4"), ("u", "f8", (3,))])
    data["id"] = 10
    data["u"] = [[[np.nan, 230.0, np.nan]]]
    result = get_effective_component_state(base, {ComponentType.node: data}, ComponentType.node, 10, 0)
    assert result["u"] == [220.0, 230.0, 222.0]


def test_effective_state_rejects_mismatched_base_id():
    with pytest.raises(ValueError, match="Base component ID"):
        get_effective_component_state({"id": 6, "from_status": 1}, make_line_updates(), ComponentType.line, 5, 0)


def test_effective_state_without_updates_returns_independent_copy():
    base = {"id": 10, "u": [220.0, 221.0, 222.0]}
    result = get_effective_component_state(base, None, ComponentType.node, 10, 0)
    result["u"][0] = 999.0
    assert base["u"][0] == 220.0


def test_sparse_scenario_lookup():
    dense = make_output_data()[ComponentType.node]
    sparse = {"indptr": np.array([0, 2, 4, 6], dtype=np.int64), "data": dense.reshape(-1).copy()}
    result = get_component_state({ComponentType.node: sparse}, ComponentType.node, 10, 1)
    assert result is not None
    assert result["u"] == [111.0, 112.0, 113.0]
    assert get_scenario_count({ComponentType.node: sparse}) == 3


def test_sparse_missing_component_returns_none():
    dense = make_output_data()[ComponentType.node]
    sparse = {"indptr": np.array([0, 2, 4, 6], dtype=np.int64), "data": dense.reshape(-1).copy()}
    assert get_component_state({ComponentType.node: sparse}, ComponentType.node, 999, 1) is None
