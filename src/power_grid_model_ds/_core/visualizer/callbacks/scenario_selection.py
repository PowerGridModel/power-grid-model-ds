# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Validate and coordinate scenario and timestamp navigation."""

from dash import Input, Output, callback, ctx, no_update

from power_grid_model_ds._core.visualizer.scenario_selection import get_scenario_count
from power_grid_model_ds._core.visualizer.server_state import (
    get_output_data,
    get_timestamps,
    get_update_data,
)


def _time_options_for_date(
    timestamps: tuple[str, ...],
    selected_date: str,
) -> list[dict[str, str | int]]:
    """Return available times with their original scenario indices."""
    return [
        {"label": timestamp[11:], "value": index}
        for index, timestamp in enumerate(timestamps)
        if timestamp[:10] == selected_date
    ]


def _valid_scenario_index(index: object, count: int) -> bool:
    """Accept only integer indices within the scenario range."""
    return type(index) is int and 0 <= index < count


def _navigate_from_scenario(
    scenario: object,
    timestamps: tuple[str, ...],
):
    """Derive timestamp controls from the scenario index."""
    if _valid_scenario_index(scenario, len(timestamps)):
        selected_date = timestamps[scenario][:10]
        return (
            no_update,
            selected_date,
            _time_options_for_date(timestamps, selected_date),
            scenario,
        )

    # Preserve invalid input so validation can display an error.
    return (no_update, None, [], None)


def _navigate_from_date(
    selected_date: str | None,
    timestamps: tuple[str, ...],
):
    """Update time options without automatically selecting a scenario."""
    if selected_date is None:
        return (None, None, [], None)

    return (
        None,
        no_update,
        _time_options_for_date(timestamps, selected_date),
        None,
    )


def _navigate_from_time(
    selected_date: str | None,
    selected_time: int | None,
    timestamps: tuple[str, ...],
):
    """Select the scenario corresponding to the chosen time."""
    if selected_time is None:
        return (None, None, [], None)

    if _valid_scenario_index(selected_time, len(timestamps)) and selected_date == timestamps[selected_time][:10]:
        return (selected_time, no_update, no_update, no_update)

    return (no_update, no_update, no_update, no_update)


def _navigate(
    trigger: str | None,
    scenario: object,
    selected_date: str | None,
    selected_time: int | None,
    timestamps: tuple[str, ...] | None,
):
    """Calculate navigation values from the triggering control."""
    unchanged = (no_update, no_update, no_update, no_update)

    if not timestamps or trigger is None:
        return unchanged

    if trigger == "scenario-selector":
        return _navigate_from_scenario(scenario, timestamps)

    if trigger == "timestamp-date":
        return _navigate_from_date(selected_date, timestamps)

    if trigger == "timestamp-time":
        return _navigate_from_time(selected_date, selected_time, timestamps)

    return unchanged


@callback(
    Output("scenario-selector", "value"),
    Output("timestamp-date", "date"),
    Output("timestamp-time", "options"),
    Output("timestamp-time", "value"),
    Input("scenario-selector", "value"),
    Input("timestamp-date", "date"),
    Input("timestamp-time", "value"),
    prevent_initial_call=True,
)
def synchronize_scenario_navigation(
    scenario: object,
    selected_date: str | None,
    selected_time: int | None,
):
    """Synchronise navigation through a single callback."""
    return _navigate(
        ctx.triggered_id,
        scenario,
        selected_date,
        selected_time,
        get_timestamps(),
    )


@callback(
    Output("scenario-validation", "children"),
    Output("scenario-validation", "className"),
    Output("scenario-selector", "style"),
    Input("scenario-selector", "value"),
)
def validate_scenario_input(value: object):
    """Validate scenario indices and highlight invalid input."""
    base_style = {"width": "100%"}
    count = get_scenario_count(get_update_data(), get_output_data())

    if value is None or value == "":
        return (
            (
                "Enter a scenario index to inspect its network state. "
                "You can inspect components normally without selecting one."
            ),
            "text-muted small mt-2",
            base_style,
        )

    if count is not None and _valid_scenario_index(value, count):
        return (
            f"Inspecting scenario {value}.",
            "text-muted small mt-2",
            base_style,
        )

    maximum = count - 1 if count else 0

    return (
        f"Invalid scenario index. Enter a whole number between 0 and {maximum}.",
        "text-danger small mt-2",
        {
            **base_style,
            "border": "2px solid #dc3545",
            "color": "#dc3545",
            "boxShadow": "0 0 0 1px #dc3545",
            "outline": "none",
        },
    )
