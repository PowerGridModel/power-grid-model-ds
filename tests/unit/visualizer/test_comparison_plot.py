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
from power_grid_model_ds._core.visualizer.measurement_comparison import (
    MeasurementComparison,
    VoltageComparison,
)


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


@pytest.fixture
def power_options():
    """Plot settings for active power measurement comparison."""
    return ComparisonPlotOptions(
        title="Active power comparison",
        quantity="active power",
        unit="W",
        sensor_id=201,
        comparison_type="sym_power_sensor",
        measurement_attribute="p_measured",
    )


def _power_comparison(sigma):
    return MeasurementComparison(
        scenario_indices=np.array([0, 1, 2]),
        measured=np.array([10.0, 10.0, 10.0]),
        estimated=np.array([9.0, 11.0, 8.0]),
        sigma=sigma,
    )


def test_power_plot_with_sigma_has_four_traces(power_options):
    figure = create_measurement_comparison_figure(
        _power_comparison(np.array([2.0, 2.0, 2.0])),
        power_options,
        sigma_multiplier=2.0,
    )

    assert len(figure.data) == 4
    np.testing.assert_allclose(figure.data[0].y, [6.0, 6.0, 6.0])
    np.testing.assert_allclose(figure.data[1].y, [14.0, 14.0, 14.0])
    np.testing.assert_allclose(figure.data[2].y, [10.0, 10.0, 10.0])
    np.testing.assert_allclose(figure.data[3].y, [9.0, 11.0, 8.0])

    assert figure.layout.meta["measurement_attribute"] == "p_measured"
    assert figure.layout.meta["sigma"] == [2.0, 2.0, 2.0]


def test_power_plot_without_sigma_has_two_traces(power_options):
    figure = create_measurement_comparison_figure(
        _power_comparison(None),
        power_options,
    )

    assert len(figure.data) == 2
    assert [trace.name for trace in figure.data] == [
        "Measured active power",
        "Calculated active power",
    ]
    assert figure.layout.meta["comparison_type"] == "sym_power_sensor"
    assert "sigma" not in figure.layout.meta


def test_power_plot_with_all_missing_sigma_has_two_traces(power_options):
    figure = create_measurement_comparison_figure(
        _power_comparison(np.array([np.nan, np.nan, np.nan])),
        power_options,
    )

    assert len(figure.data) == 2


def test_power_plot_preserves_partial_sigma(power_options):
    figure = create_measurement_comparison_figure(
        _power_comparison(np.array([2.0, np.nan, 1.0])),
        power_options,
        sigma_multiplier=2.0,
    )

    assert len(figure.data) == 4
    np.testing.assert_allclose(
        figure.data[0].y,
        [6.0, np.nan, 8.0],
        equal_nan=True,
    )
    np.testing.assert_allclose(
        figure.data[1].y,
        [14.0, np.nan, 12.0],
        equal_nan=True,
    )


def test_power_plot_rejects_invalid_multiplier(power_options):
    with pytest.raises(ValueError, match="Sigma multiplier"):
        create_measurement_comparison_figure(
            _power_comparison(None),
            power_options,
            sigma_multiplier=-1.0,
        )
