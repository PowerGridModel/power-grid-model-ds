# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Reusable measured-versus-estimated comparison figures."""

import plotly.graph_objects as go

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    MeasurementComparison,
    get_measurement_sigma_bounds,
)


def create_measurement_comparison_figure(  # noqa: PLR0913
    comparison: MeasurementComparison,
    *,
    title: str,
    quantity: str,
    unit: str,
    sigma_multiplier: float = 2.0,
    estimated_label: str = "Calculated",
) -> go.Figure:
    """Plot aligned series, with measurement-centred bands when sigma exists."""
    fig = go.Figure()

    if comparison.sigma is not None:
        lower, upper = get_measurement_sigma_bounds(comparison, sigma_multiplier)
        fig.add_trace(
            go.Scatter(
                x=comparison.scenario_indices,
                y=lower,
                mode="lines",
                line={"width": 0},
                showlegend=False,
                hoverinfo="skip",
                name="Lower sigma bound",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=comparison.scenario_indices,
                y=upper,
                mode="lines",
                line={"width": 0},
                fill="tonexty",
                fillcolor="rgba(100, 149, 237, 0.20)",
                name=f"Measurement +/- {sigma_multiplier:g} sigma",
                hoverinfo="skip",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=comparison.measured,
            mode="lines",
            name=f"Measured {quantity}",
            line={"width": 2, "color": "royalblue"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=comparison.estimated,
            mode="lines",
            name=f"{estimated_label} {quantity}",
            line={"width": 2, "color": "darkorange", "dash": "dash"},
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Scenario Index",
        yaxis_title=f"{quantity.capitalize()} ({unit})" if unit else quantity.capitalize(),
        template="plotly_white",
        hovermode="x unified",
        showlegend=True,
    )
    return fig
