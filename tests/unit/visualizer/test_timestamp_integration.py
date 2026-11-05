"""Tests for F05 timestamp integration with the visualizer entry point."""

from unittest.mock import patch

import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds.visualizer import visualize


def make_grid():
    return Grid.from_txt("S1 2 12", "2 3 23")


def make_output_data():
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (2, 1))
    nodes["id"] = [[1], [1]]
    return {ComponentType.node: nodes}


def test_server_state_stores_timestamps():
    timestamps = ("2026-11-05T09:00:00+01:00",)
    server_state.set_app_state(make_grid(), timestamps=timestamps)
    assert server_state.get_timestamps() == timestamps


def test_server_state_resets_timestamps():
    server_state.set_app_state(
        make_grid(),
        timestamps=("2026-11-05T09:00:00+01:00",),
    )
    server_state.set_app_state(make_grid())
    assert server_state.get_timestamps() is None


def test_visualize_passes_validated_timestamps_to_state():
    timestamps = [
        "2026-11-05T09:00:00+01:00",
        "2026-11-05T09:15:00+01:00",
    ]

    with patch("power_grid_model_ds.visualizer.Dash") as dash:
        visualize(
            grid=make_grid(),
            output_data=make_output_data(),
            timestamps=timestamps,
        )

    assert server_state.get_timestamps() == tuple(timestamps)
    dash.return_value.run.assert_called_once()


def test_visualize_rejects_mismatched_timestamp_count():
    with (
        patch("power_grid_model_ds.visualizer.Dash") as dash,
        pytest.raises(ValueError, match="timestamps"),
    ):
        visualize(
            grid=make_grid(),
            output_data=make_output_data(),
            timestamps=["2026-11-05T09:00:00+01:00"],
        )

    dash.assert_not_called()


def test_visualize_without_timestamps_preserves_existing_api():
    with patch("power_grid_model_ds.visualizer.Dash") as dash:
        visualize(grid=make_grid())

    assert server_state.get_timestamps() is None
    dash.return_value.run.assert_called_once()
