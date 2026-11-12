# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for reusable measurement comparison plotting."""

import numpy as np
import pytest

from power_grid_model_ds._core.visualizer.comparison_plot import (
    ComparisonPlotOptions,
    create_measurement_comparison_figure,
)
from power_grid_model_ds._core.visualizer.measurement_comparison import VoltageComparison


@pytest.fixture
def comparison():
    """Aligned measured, calculated, and uncertainty values."""
    return VoltageComparison(
        scenario_indices=np.array([0, 1, 2]),
        measured=np.array([230.0, 235.0, 230.0]),
        estimated=np.array([229.0, 231.0, 228.0]),
        sigma=np.array([2.0, 3.0, 2.0]),
    )


@pytest.fixture
def options():
    return ComparisonPlotOptions(
        title="Voltage comparison",
        quantity="voltage",
        unit="V",
        sensor_id=101,
        comparison_type="sym_voltage_sensor",
    )


def test_shared_plotter_preserves_trace_order(comparison, options):
    figure = create_measurement_comparison_figure(comparison, options)

    assert len(figure.data) == 4
    assert [trace.name for trace in figure.data] == [
        "Lower sigma bound",
        "Measurement +/- 3 sigma",
        "Measured voltage",
        "Calculated voltage",
    ]


def test_shared_plotter_uses_default_three_sigma(comparison, options):
    figure = create_measurement_comparison_figure(comparison, options)

    np.testing.assert_allclose(figure.data[0].y, [224.0, 226.0, 224.0])
    np.testing.assert_allclose(figure.data[1].y, [236.0, 244.0, 236.0])


def test_shared_plotter_supports_custom_multiplier(comparison, options):
    figure = create_measurement_comparison_figure(
        comparison,
        options,
        sigma_multiplier=2.0,
    )

    np.testing.assert_allclose(figure.data[0].y, [226.0, 229.0, 226.0])
    np.testing.assert_allclose(figure.data[1].y, [234.0, 241.0, 234.0])
    assert figure.data[1].name == "Measurement +/- 2 sigma"


def test_shared_plotter_preserves_metadata(comparison, options):
    figure = create_measurement_comparison_figure(comparison, options)

    assert figure.layout.meta == {
        "comparison_type": "sym_voltage_sensor",
        "sensor_id": 101,
        "sigma": [2.0, 3.0, 2.0],
        "measured": [230.0, 235.0, 230.0],
    }
    assert figure.layout.yaxis.title.text == "Voltage (V)"


def test_shared_plotter_preserves_missing_values(options):
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 230.0]),
        estimated=np.array([229.0, np.nan]),
        sigma=np.array([2.0, np.nan]),
    )

    figure = create_measurement_comparison_figure(comparison, options)

    assert np.isnan(figure.data[0].y[1])
    assert np.isnan(figure.data[1].y[1])
    assert np.isnan(figure.data[3].y[1])
