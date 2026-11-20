# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Reusable measured-versus-calculated comparison figures."""

from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    MeasurementComparison,
    VoltageComparison,
    get_voltage_sigma_bounds,
)


@dataclass(frozen=True)
class ComparisonPlotOptions:
    """Presentation settings for a measurement comparison."""

    title: str
    quantity: str
    unit: str
    sensor_id: int | None = None
    comparison_type: str | None = None
    measurement_attribute: str | None = None


def create_measurement_comparison_figure(
    comparison: VoltageComparison | MeasurementComparison,
    options: ComparisonPlotOptions,
    sigma_multiplier: float = 3.0,
) -> go.Figure:
    """Plot measured and calculated values with optional sigma bands."""
    if not np.isfinite(sigma_multiplier) or sigma_multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    sigma = comparison.sigma
    has_sigma = sigma is not None and np.any(np.isfinite(sigma))

    fig = go.Figure()

    if has_sigma:
        lower, upper = get_voltage_sigma_bounds(comparison, sigma_multiplier)

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
            name=f"Measured {options.quantity}",
            line={"width": 2, "color": "royalblue"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=comparison.estimated,
            mode="lines",
            name=f"Calculated {options.quantity}",
            line={"width": 2, "color": "darkorange", "dash": "dash"},
        )
    )

    layout = {
        "title": options.title,
        "xaxis_title": "Scenario Index",
        "yaxis_title": (
            f"{options.quantity.capitalize()} ({options.unit})" if options.unit else options.quantity.capitalize()
        ),
        "template": "plotly_white",
        "hovermode": "x unified",
        "showlegend": True,
    }

    if options.sensor_id is not None and options.comparison_type is not None:
        meta = {
            "comparison_type": options.comparison_type,
            "sensor_id": options.sensor_id,
        }

        if options.measurement_attribute is not None:
            meta["measurement_attribute"] = options.measurement_attribute

        if has_sigma:
            meta["sigma"] = sigma.tolist()
            meta["measured"] = comparison.measured.tolist()

        layout["meta"] = meta

    fig.update_layout(**layout)
    return fig
