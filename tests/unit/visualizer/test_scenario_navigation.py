# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for scenario and optional timestamp navigation."""

from unittest.mock import patch

import pytest
from dash import no_update

from power_grid_model_ds._core.visualizer.callbacks.scenario_selection import (
    _navigate,
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

CALLBACK_MODULE = "power_grid_model_ds._core.visualizer.callbacks.scenario_selection"
TIMESTAMPS = (
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
    "2026-11-05T09:30:00+01:00",
    "2026-11-05T09:45:00+01:00",
)
TIME_OPTIONS = [{"label": timestamp[11:], "value": index} for index, timestamp in enumerate(TIMESTAMPS)]
UNCHANGED = (no_update, no_update, no_update, no_update)


def _assert_navigation(actual, expected):
    assert len(actual) == len(expected) == 4
    for result, wanted in zip(actual, expected, strict=True):
        if wanted is no_update:
            assert result is no_update
        else:
            assert result == wanted


def test_available_dates():
    assert _available_dates(TIMESTAMPS) == ["2026-11-05"]


def test_disabled_dates():
    assert _disabled_dates(["2026-11-05", "2026-11-07"]) == ["2026-11-06"]


def test_available_times_retain_scenario_indices():
    assert _time_options(TIMESTAMPS, "2026-11-05") == TIME_OPTIONS
    assert _time_options_for_date(TIMESTAMPS, "2026-11-05") == TIME_OPTIONS
    assert _time_options_for_date(TIMESTAMPS, "2026-11-06") == []


def test_distinct_timezone_offsets_remain_distinguishable():
    timestamps = (
        "2026-10-25T02:30:00+02:00",
        "2026-10-25T02:30:00+01:00",
    )
    expected = [
        {"label": "02:30:00+02:00", "value": 0},
        {"label": "02:30:00+01:00", "value": 1},
    ]
    assert _time_options_for_date(timestamps, "2026-10-25") == expected


@pytest.mark.parametrize(
    ("index", "valid"),
    [
        (0, True),
        (1, True),
        (3, True),
        (4, False),
        (-1, False),
        (None, False),
        (True, False),
        (1.5, False),
        ("1", False),
    ],
)
def test_scenario_index_validation(index, valid):
    assert _valid_scenario_index(index, 4) is valid


def test_enter_scenario_populates_date_and_time():
    _assert_navigation(
        _navigate_from_scenario(1, TIMESTAMPS),
        (no_update, "2026-11-05", TIME_OPTIONS, 1),
    )


@pytest.mark.parametrize("scenario", [None, -1, 4, 1.5])
def test_clearing_or_invalid_scenario_clears_timestamp_controls(scenario):
    _assert_navigation(
        _navigate_from_scenario(scenario, TIMESTAMPS),
        (no_update, None, [], None),
    )


def test_select_date_populates_times_without_choosing_scenario():
    _assert_navigation(
        _navigate_from_date("2026-11-05", TIMESTAMPS),
        (None, no_update, TIME_OPTIONS, None),
    )


def test_clear_date_clears_every_field():
    _assert_navigation(_navigate_from_date(None, TIMESTAMPS), (None, None, [], None))


def test_select_time_sets_matching_scenario():
    _assert_navigation(
        _navigate_from_time("2026-11-05", 1, TIMESTAMPS),
        (1, no_update, no_update, no_update),
    )


def test_clear_time_clears_every_field():
    _assert_navigation(_navigate_from_time("2026-11-05", None, TIMESTAMPS), (None, None, [], None))


@pytest.mark.parametrize(
    ("selected_date", "selected_time"),
    [("2026-11-06", 1), ("2026-11-05", 4)],
)
def test_invalid_time_selection_does_not_change_navigation(selected_date, selected_time):
    _assert_navigation(
        _navigate_from_time(selected_date, selected_time, TIMESTAMPS),
        UNCHANGED,
    )


@pytest.mark.parametrize("timestamps", [None, ()])
def test_no_timestamps_does_not_change_scenario(timestamps):
    _assert_navigation(_navigate("scenario-selector", 1, None, None, timestamps), UNCHANGED)


def test_unknown_trigger_does_not_change_navigation():
    _assert_navigation(_navigate("unknown", 1, None, None, TIMESTAMPS), UNCHANGED)


def test_initial_navigation_does_not_change_fields():
    _assert_navigation(_navigate(None, 1, None, None, TIMESTAMPS), UNCHANGED)


@pytest.mark.parametrize(
    ("trigger", "scenario", "date_value", "time_value", "expected"),
    [
        ("scenario-selector", 1, None, None, (no_update, "2026-11-05", TIME_OPTIONS, 1)),
        ("timestamp-date", 1, "2026-11-05", 1, (None, no_update, TIME_OPTIONS, None)),
        ("timestamp-date", 1, None, 1, (None, None, [], None)),
        ("timestamp-time", None, "2026-11-05", 1, (1, no_update, no_update, no_update)),
        ("timestamp-time", 1, "2026-11-05", None, (None, None, [], None)),
    ],
)
def test_navigation_dispatch(trigger, scenario, date_value, time_value, expected):
    _assert_navigation(_navigate(trigger, scenario, date_value, time_value, TIMESTAMPS), expected)


def test_callback_dispatches_scenario_selection():
    with (
        patch(f"{CALLBACK_MODULE}.get_timestamps", return_value=TIMESTAMPS),
        patch(f"{CALLBACK_MODULE}.ctx") as mock_ctx,
    ):
        mock_ctx.triggered_id = "scenario-selector"
        result = synchronize_scenario_navigation(1, None, None)
    _assert_navigation(result, (no_update, "2026-11-05", TIME_OPTIONS, 1))


@pytest.mark.parametrize("value", [None, ""])
def test_empty_scenario_has_neutral_validation(value):
    with (
        patch(f"{CALLBACK_MODULE}.get_scenario_count", return_value=4),
        patch(f"{CALLBACK_MODULE}.get_update_data", return_value=None),
        patch(f"{CALLBACK_MODULE}.get_output_data", return_value=None),
    ):
        message, css_class, style = validate_scenario_input(value)
    assert "Enter a scenario index" in message
    assert "text-muted" in css_class
    assert style == {"width": "100%"}


def test_valid_scenario_has_neutral_validation():
    with (
        patch(f"{CALLBACK_MODULE}.get_scenario_count", return_value=4),
        patch(f"{CALLBACK_MODULE}.get_update_data", return_value=None),
        patch(f"{CALLBACK_MODULE}.get_output_data", return_value=None),
    ):
        message, css_class, style = validate_scenario_input(1)
    assert message == "Inspecting scenario 1."
    assert "text-muted" in css_class
    assert style == {"width": "100%"}


@pytest.mark.parametrize("value", [-1, 4, 1.5, True])
def test_invalid_scenario_has_red_border(value):
    with (
        patch(f"{CALLBACK_MODULE}.get_scenario_count", return_value=4),
        patch(f"{CALLBACK_MODULE}.get_update_data", return_value=None),
        patch(f"{CALLBACK_MODULE}.get_output_data", return_value=None),
    ):
        message, css_class, style = validate_scenario_input(value)
    assert "between 0 and 3" in message
    assert "text-danger" in css_class
    assert style["border"] == "2px solid #dc3545"
    assert style["color"] == "#dc3545"
    assert style["boxShadow"] == "0 0 0 1px #dc3545"
