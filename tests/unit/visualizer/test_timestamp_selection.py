"""Tests for F05 timestamp-to-scenario selection."""

import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer.timestamp_selection import (
    get_component_state,
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
    data = make_output_data()

    result = get_component_state(
        data,
        ComponentType.node,
        component_id=10,
        scenario_index=1,
    )

    assert result is not None
    assert np.array_equal(result["u"], [111.0, 112.0, 113.0])


def test_component_lookup_returns_none_for_missing_component():
    data = make_output_data()

    result = get_component_state(
        data,
        ComponentType.node,
        component_id=999,
        scenario_index=1,
    )

    assert result is None


def test_component_lookup_rejects_invalid_scenario_index():
    data = make_output_data()

    with pytest.raises(IndexError):
        get_component_state(
            data,
            ComponentType.node,
            component_id=10,
            scenario_index=3,
        )
