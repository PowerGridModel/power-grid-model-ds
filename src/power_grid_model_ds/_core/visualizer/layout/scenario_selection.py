# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Optional scenario-index selection and timestamp navigation."""

from datetime import date, timedelta

from dash import dcc, html

from power_grid_model_ds._core.visualizer.scenario_selection import get_scenario_count
from power_grid_model_ds._core.visualizer.server_state import get_output_data, get_timestamps, get_update_data


def _available_dates(timestamps: tuple[str, ...]) -> list[str]:
    """Return distinct calendar dates in chronological order."""
    return sorted({timestamp[:10] for timestamp in timestamps})


def _disabled_dates(dates: list[str]) -> list[str]:
    """Disable dates without observations within the available date range."""
    first = date.fromisoformat(dates[0])
    last = date.fromisoformat(dates[-1])
    available = set(dates)
    return [
        (first + timedelta(days=offset)).isoformat()
        for offset in range((last - first).days + 1)
        if (first + timedelta(days=offset)).isoformat() not in available
    ]


def _time_options(timestamps: tuple[str, ...], selected_date: str) -> list[dict[str, str | int]]:
    """Map available times to their original scenario indices."""
    return [
        {"label": timestamp[11:], "value": index}
        for index, timestamp in enumerate(timestamps)
        if timestamp[:10] == selected_date
    ]


def get_scenario_selection_html() -> html.Div:
    """Render optional scenario selection without activating a scenario."""
    timestamps = get_timestamps()
    count = get_scenario_count(get_update_data(), get_output_data())
    if count is None or count == 0:
        return html.Div(id="timestamp-selection-container")

    children = [
        html.Div(
            [
                html.H4("Network state", className="mb-1"),
                html.P("Optional scenario-based investigation", className="text-muted mb-0"),
            ],
            className="mb-3",
        ),
        html.Label(
            "Scenario index",
            htmlFor="scenario-selector",
            className="form-label fw-semibold",
        ),
        dcc.Input(
            id="scenario-selector",
            type="number",
            step=1,
            value=None,
            placeholder="e.g. 0",
            debounce=False,
            className="form-control",
            style={"width": "100%"},
        ),
        html.Div(
            id="scenario-validation",
            children=(
                "Enter a scenario index to inspect its network state. "
                "You can inspect components normally without selecting one."
            ),
            className="text-muted small mt-2",
        ),
    ]

    if timestamps:
        dates = _available_dates(timestamps)
        children.append(
            html.Div(
                [
                    html.P("Optional timestamp navigation", className="fw-semibold mb-2"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Observation date",
                                        htmlFor="timestamp-date",
                                        className="form-label",
                                    ),
                                    dcc.DatePickerSingle(
                                        id="timestamp-date",
                                        date=None,
                                        min_date_allowed=dates[0],
                                        max_date_allowed=dates[-1],
                                        disabled_days=_disabled_dates(dates),
                                        display_format="DD MMM YYYY",
                                        clearable=True,
                                        first_day_of_week=1,
                                        number_of_months_shown=1,
                                    ),
                                ],
                                className="col-12 col-md-6",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Available time",
                                        htmlFor="timestamp-time",
                                        className="form-label",
                                    ),
                                    dcc.Dropdown(
                                        id="timestamp-time",
                                        options=[],
                                        value=None,
                                        clearable=True,
                                        placeholder="Choose an available time",
                                    ),
                                ],
                                className="col-12 col-md-6",
                            ),
                        ],
                        className="row g-3 align-items-end",
                    ),
                ],
                className="mt-3",
            )
        )

    return html.Div(
        children,
        id="timestamp-selection-container",
        className="card shadow-sm border-0",
        style={"padding": "24px", "margin": "16px 0", "borderRadius": "12px"},
    )
