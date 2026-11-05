"""Tests for the F05 calendar and available-time selection."""

from unittest.mock import patch

from power_grid_model_ds._core.visualizer.callbacks.timestamp_selection import (
    update_available_times,
    update_selected_scenario,
)
from power_grid_model_ds._core.visualizer.layout.timestamp_selection import (
    _available_dates,
    _disabled_dates,
    _time_options,
)

TIMESTAMPS = (
    "2026-10-31T23:45:00+01:00",
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
    "2026-11-05T09:30:00+01:00",
)


def test_available_dates_across_months():
    assert _available_dates(TIMESTAMPS) == [
        "2026-10-31",
        "2026-11-05",
    ]


def test_missing_dates_are_disabled():
    assert _disabled_dates(["2026-10-31", "2026-11-05"]) == [
        "2026-11-01",
        "2026-11-02",
        "2026-11-03",
        "2026-11-04",
    ]


def test_time_options_preserve_scenario_indices():
    assert _time_options(TIMESTAMPS, "2026-11-05") == [
        {"label": "09:00:00+01:00", "value": 1},
        {"label": "09:15:00+01:00", "value": 2},
        {"label": "09:30:00+01:00", "value": 3},
    ]


def test_calendar_date_selects_first_available_time():
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.timestamp_selection.get_timestamps",
        return_value=TIMESTAMPS,
    ):
        options, selected = update_available_times("2026-11-05")

    assert len(options) == 3
    assert selected == 1


def test_calendar_date_without_data():
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.timestamp_selection.get_timestamps",
        return_value=TIMESTAMPS,
    ):
        options, selected = update_available_times("2026-11-02")

    assert options == []
    assert selected is None


def test_scenario_selection_preserves_original_index():
    with patch(
        "power_grid_model_ds._core.visualizer.callbacks.timestamp_selection.get_timestamps",
        return_value=TIMESTAMPS,
    ):
        assert update_selected_scenario(3) == 3
        assert update_selected_scenario(4) is None
        assert update_selected_scenario(None) is None


def test_time_options_keep_distinct_timezone_offsets():
    timestamps = (
        "2026-10-25T02:30:00+02:00",
        "2026-10-25T02:30:00+01:00",
    )

    assert _time_options(timestamps, "2026-10-25") == [
        {"label": "02:30:00+02:00", "value": 0},
        {"label": "02:30:00+01:00", "value": 1},
    ]
