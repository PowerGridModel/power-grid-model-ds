# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Validate optional scenario selection and synchronize timestamp navigation."""

from dash import Input, Output, callback, ctx, no_update, set_props

from power_grid_model_ds._core.visualizer.scenario_selection import get_scenario_count
from power_grid_model_ds._core.visualizer.server_state import get_output_data, get_timestamps, get_update_data


def _time_options_for_date(timestamps: tuple[str, ...], selected_date: str) -> list[dict[str, str | int]]:
    """Return available times using original scenario indices."""
    return [
        {"label": timestamp[11:], "value": index}
        for index, timestamp in enumerate(timestamps)
        if timestamp[:10] == selected_date
    ]


def _valid_scenario_index(index: object, count: int) -> bool:
    """Accept only integer scenario indices within the batch range."""
    return type(index) is int and 0 <= index < count


def _clear_timestamp_navigation() -> None:
    """Reset optional timestamp controls without selecting a scenario."""
    if get_timestamps():
        set_props("timestamp-date", {"date": None})
        set_props("timestamp-time", {"options": [], "value": None})


def _navigate_from_scenario(timestamps: tuple[str, ...], scenario_index: int | None) -> None:
    """Update timestamp controls only after a valid scenario is selected."""
    if not _valid_scenario_index(scenario_index, len(timestamps)):
        return

    selected_date = timestamps[scenario_index][:10]
    set_props("timestamp-date", {"date": selected_date})
    set_props(
        "timestamp-time",
        {"options": _time_options_for_date(timestamps, selected_date), "value": scenario_index},
    )


def _navigate_from_date(timestamps: tuple[str, ...], selected_date: str | None) -> int | None:
    """Choose the first scenario on a user-selected date."""
    if selected_date is None:
        return no_update

    options = _time_options_for_date(timestamps, selected_date)
    if not options:
        return no_update

    first_index = int(options[0]["value"])
    set_props("timestamp-time", {"options": options, "value": first_index})
    return first_index


def _navigate_from_time(timestamps: tuple[str, ...], selected_time: int | None) -> int | None:
    """Map a selected time to its scenario index."""
    if not _valid_scenario_index(selected_time, len(timestamps)):
        return no_update
    return selected_time


@callback(
    Output("scenario-selector", "value"),
    Input("timestamp-date", "date", allow_optional=True),
    Input("timestamp-time", "value", allow_optional=True),
    prevent_initial_call=True,
)
def synchronize_scenario_navigation(
    selected_date: str | None,
    selected_time: int | None,
) -> int | None:
    """Apply date/time navigation without automatically selecting a scenario."""
    timestamps = get_timestamps()
    if not timestamps:
        return no_update

    triggered = ctx.triggered_id
    if triggered == "timestamp-date":
        return _navigate_from_date(timestamps, selected_date)
    if triggered == "timestamp-time":
        return _navigate_from_time(timestamps, selected_time)

    return no_update


@callback(
    Output("scenario-validation", "children"),
    Output("scenario-validation", "className"),
    Output("scenario-selector", "style"),
    Input("scenario-selector", "value"),
)
def validate_scenario_input(value: object):
    """Validate the index and visibly highlight invalid input."""
    base_style = {"width": "100%"}
    count = get_scenario_count(get_update_data(), get_output_data())

    if value is None or value == "":
        _clear_timestamp_navigation()
        return (
            (
                "Enter a scenario index to inspect its network state. "
                "You can inspect components normally without selecting one."
            ),
            "text-muted small mt-2",
            base_style,
        )

    if count is not None and _valid_scenario_index(value, count):
        timestamps = get_timestamps()
        if timestamps:
            _navigate_from_scenario(timestamps, value)
        return (
            f"Inspecting scenario {value}.",
            "text-muted small mt-2",
            base_style,
        )

    _clear_timestamp_navigation()
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
