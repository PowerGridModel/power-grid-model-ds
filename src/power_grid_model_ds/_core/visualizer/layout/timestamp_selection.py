"""F05 date-and-time selection layout."""

from datetime import date, timedelta

from dash import dcc, html

from power_grid_model_ds._core.visualizer.server_state import get_timestamps


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
    """Map the selected date's available times to original scenario indices."""
    return [
        {
            "label": timestamp[11:],
            "value": index,
        }
        for index, timestamp in enumerate(timestamps)
        if timestamp[:10] == selected_date
    ]


def get_timestamp_selection_html() -> html.Div:
    """Build a calendar and time selector when timestamps are available."""
    timestamps = get_timestamps()

    if timestamps is None:
        return html.Div(id="timestamp-selection-container")

    dates = _available_dates(timestamps)
    initial_date = timestamps[0][:10]
    initial_options = _time_options(timestamps, initial_date)

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H4(
                                "Network state",
                                className="mb-1",
                            ),
                            html.P(
                                "Inspect network components at an available timestamp.",
                                className="text-muted mb-0",
                            ),
                        ]
                    ),
                    html.I(
                        className="fas fa-clock text-secondary",
                        style={"fontSize": "22px"},
                    ),
                ],
                className="d-flex justify-content-between align-items-center mb-4",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                "Observation date",
                                htmlFor="timestamp-date",
                                className="form-label fw-semibold",
                            ),
                            dcc.DatePickerSingle(
                                id="timestamp-date",
                                date=initial_date,
                                min_date_allowed=dates[0],
                                max_date_allowed=dates[-1],
                                disabled_days=_disabled_dates(dates),
                                display_format="DD MMM YYYY",
                                clearable=False,
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
                                className="form-label fw-semibold",
                            ),
                            dcc.Dropdown(
                                id="timestamp-time",
                                options=initial_options,
                                value=initial_options[0]["value"],
                                clearable=False,
                                searchable=True,
                            ),
                        ],
                        className="col-12 col-md-6",
                    ),
                ],
                className="row g-3 align-items-end",
            ),
            dcc.Dropdown(
                id="timestamp-selector",
                options=[{"label": timestamp, "value": index} for index, timestamp in enumerate(timestamps)],
                value=0,
                clearable=False,
                style={"display": "none"},
            ),
            html.Hr(className="my-4"),
            html.Div(
                id="timestamp-state-output",
                children=None,
            ),
        ],
        id="timestamp-selection-container",
        className="card shadow-sm border-0",
        style={
            "padding": "24px",
            "margin": "16px 0",
            "borderRadius": "12px",
        },
    )
