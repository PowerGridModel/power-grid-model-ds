# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for optional scenario-index and timestamp navigation."""

from unittest.mock import call, patch

import pytest
from dash import no_update

from power_grid_model_ds._core.visualizer.callbacks.scenario_selection import (
    _clear_timestamp_navigation,
    _navigate_from_date,
    _navigate_from_scenario,
    _navigate_from_time,
    _time_options_for_date,
    _valid_scenario_index,
    synchronize_scenario_navigation,
    validate_scenario_input,
)
from power_grid_model_ds._core.visualizer.layout.scenario_selection import (
    _available_dates,
    _disabled_dates,
    _time_options,
)

MODULE = "power_grid_model_ds._core.visualizer.callbacks.scenario_selection"

TIMESTAMPS = (
    "2026-10-31T23:45:00+01:00",
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
    "2026-11-05T09:30:00+01:00",
)

NOVEMBER_OPTIONS = [
    {"label": "09:00:00+01:00", "value": 1},
    {"label": "09:15:00+01:00", "value": 2},
    {"label": "09:30:00+01:00", "value": 3},
]


def test_available_dates_across_months():
    assert _available_dates(TIMESTAMPS) == ["2026-10-31", "2026-11-05"]


def test_missing_dates_are_disabled():
    assert _disabled_dates(["2026-10-31", "2026-11-05"]) == [
        "2026-11-01",
        "2026-11-02",
        "2026-11-03",
        "2026-11-04",
    ]


def test_time_options_preserve_scenario_indices():
    assert _time_options(TIMESTAMPS, "2026-11-05") == NOVEMBER_OPTIONS
    assert _time_options_for_date(TIMESTAMPS, "2026-11-05") == NOVEMBER_OPTIONS


def test_time_options_keep_distinct_timezone_offsets():
    timestamps = (
        "2026-10-25T02:30:00+02:00",
        "2026-10-25T02:30:00+01:00",
    )
    expected = [
        {"label": "02:30:00+02:00", "value": 0},
        {"label": "02:30:00+01:00", "value": 1},
    ]
    assert _time_options(timestamps, "2026-10-25") == expected
    assert _time_options_for_date(timestamps, "2026-10-25") == expected


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (0, True),
        (3, True),
        (4, False),
        (-1, False),
        (None, False),
        (True, False),
        (1.5, False),
    ],
)
def test_valid_scenario_index(index, expected):
    assert _valid_scenario_index(index, len(TIMESTAMPS)) is expected


def test_scenario_selection_updates_timestamp_controls():
    with patch(f"{MODULE}.set_props") as mock_set_props:
        result = _navigate_from_scenario(TIMESTAMPS, 3)

    assert result is None
    assert mock_set_props.call_args_list == [
        call("timestamp-date", {"date": "2026-11-05"}),
        call("timestamp-time", {"options": NOVEMBER_OPTIONS, "value": 3}),
    ]


def test_invalid_scenario_does_not_update_controls():
    with patch(f"{MODULE}.set_props") as mock_set_props:
        result = _navigate_from_scenario(TIMESTAMPS, 4)

    assert result is None
    mock_set_props.assert_not_called()


def test_calendar_date_updates_times_without_selecting_scenario():
    with patch(f"{MODULE}.set_props") as mock_set_props:
        result = _navigate_from_date(TIMESTAMPS, "2026-11-05")

    assert result is no_update
    mock_set_props.assert_called_once_with(
        "timestamp-time",
        {"options": NOVEMBER_OPTIONS, "value": None},
    )


@pytest.mark.parametrize("selected_date", [None, "2026-11-02"])
def test_calendar_date_without_available_data(selected_date):
    with patch(f"{MODULE}.set_props") as mock_set_props:
        result = _navigate_from_date(TIMESTAMPS, selected_date)

    assert result is no_update
    mock_set_props.assert_not_called()


def test_time_selection_preserves_original_scenario_index():
    assert _navigate_from_time(TIMESTAMPS, 3) == 3
    assert _navigate_from_time(TIMESTAMPS, 4) is no_update
    assert _navigate_from_time(TIMESTAMPS, None) is no_update


@pytest.mark.parametrize(
    ("triggered_id", "selected_time", "expected"),
    [
        ("timestamp-time", 3, 3),
        ("timestamp-time", None, no_update),
        ("timestamp-time", 4, no_update),
        ("unknown", 3, no_update),
    ],
)
def test_navigation_dispatch(triggered_id, selected_time, expected):
    """Only a valid time selection may navigate to a scenario."""
    with (
        patch(f"{MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{MODULE}.ctx") as mock_ctx,
    ):
        mock_ctx.triggered_id = triggered_id
        result = synchronize_scenario_navigation(selected_time)

    if expected is no_update:
        assert result is no_update
    else:
        assert result == expected


@pytest.mark.parametrize("timestamps", [None, ()])
def test_navigation_without_timestamps(timestamps):
    """Timestamp navigation must remain optional."""
    with (
        patch(f"{MODULE}.get_timestamps", return_value=timestamps),
        patch(f"{MODULE}.ctx") as mock_ctx,
    ):
        mock_ctx.triggered_id = "timestamp-time"
        result = synchronize_scenario_navigation(0)

    assert result is no_update


def test_clear_timestamp_navigation():
    with (
        patch(f"{MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        result = _clear_timestamp_navigation()

    assert result is None
    assert mock_set_props.call_args_list == [
        call("timestamp-date", {"date": None}),
        call("timestamp-time", {"options": [], "value": None}),
    ]


@pytest.mark.parametrize("timestamps", [None, ()])
def test_clear_timestamp_navigation_without_timestamps(timestamps):
    with (
        patch(f"{MODULE}.get_timestamps", return_value=timestamps),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        _clear_timestamp_navigation()

    mock_set_props.assert_not_called()


@pytest.mark.parametrize("value", [None, ""])
def test_empty_scenario_resets_timestamp_controls(value):
    """Clearing the numeric input must remove timestamp selection."""
    with (
        patch(f"{MODULE}.get_scenario_count", return_value=4),
        patch(f"{MODULE}.get_update_data", return_value=None),
        patch(f"{MODULE}.get_output_data", return_value=None),
        patch(f"{MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        message, class_name, style = validate_scenario_input(value)

    assert "Enter a scenario index" in message
    assert "text-muted" in class_name
    assert style == {"width": "100%"}
    assert mock_set_props.call_args_list == [
        call("timestamp-date", {"date": None}),
        call("timestamp-time", {"options": [], "value": None}),
    ]


def test_empty_scenario_without_timestamps():
    with (
        patch(f"{MODULE}.get_scenario_count", return_value=4),
        patch(f"{MODULE}.get_update_data", return_value=None),
        patch(f"{MODULE}.get_output_data", return_value=None),
        patch(f"{MODULE}.get_timestamps", return_value=None),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        message, class_name, style = validate_scenario_input(None)

    assert "Enter a scenario index" in message
    assert "text-muted" in class_name
    assert style == {"width": "100%"}
    mock_set_props.assert_not_called()


def test_valid_scenario_synchronizes_timestamps():
    with (
        patch(f"{MODULE}.get_scenario_count", return_value=4),
        patch(f"{MODULE}.get_update_data", return_value=None),
        patch(f"{MODULE}.get_output_data", return_value=None),
        patch(f"{MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        message, class_name, style = validate_scenario_input(2)

    assert "scenario 2" in message
    assert "text-muted" in class_name
    assert style == {"width": "100%"}
    assert mock_set_props.call_args_list == [
        call("timestamp-date", {"date": "2026-11-05"}),
        call("timestamp-time", {"options": NOVEMBER_OPTIONS, "value": 2}),
    ]


@pytest.mark.parametrize("value", [-1, 4, 1.5, True])
def test_invalid_scenario_highlights_entire_border(value):
    """Invalid indices must produce a full red border and error message."""
    with (
        patch(f"{MODULE}.get_scenario_count", return_value=4),
        patch(f"{MODULE}.get_update_data", return_value=None),
        patch(f"{MODULE}.get_output_data", return_value=None),
        patch(f"{MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        message, class_name, style = validate_scenario_input(value)

    assert "between 0 and 3" in message
    assert "text-danger" in class_name
    assert style["border"] == "2px solid #dc3545"
    assert style["color"] == "#dc3545"
    assert style["boxShadow"] == "0 0 0 1px #dc3545"
    assert mock_set_props.call_args_list == [
        call("timestamp-date", {"date": None}),
        call("timestamp-time", {"options": [], "value": None}),
    ]


def test_invalid_scenario_without_timestamps():
    with (
        patch(f"{MODULE}.get_scenario_count", return_value=4),
        patch(f"{MODULE}.get_update_data", return_value=None),
        patch(f"{MODULE}.get_output_data", return_value=None),
        patch(f"{MODULE}.get_timestamps", return_value=None),
        patch(f"{MODULE}.set_props") as mock_set_props,
    ):
        message, class_name, style = validate_scenario_input(99)

    assert "Invalid scenario index" in message
    assert "text-danger" in class_name
    assert style["border"] == "2px solid #dc3545"
    mock_set_props.assert_not_called()
