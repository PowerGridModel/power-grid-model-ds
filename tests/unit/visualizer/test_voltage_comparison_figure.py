# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    _create_voltage_comparison_figure,
)
from power_grid_model_ds._core.visualizer.measurement_comparison import VoltageComparison


def test_voltage_comparison_figure_contains_sigma_bands():
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1, 2]),
        measured=np.array([230.0, 235.0, 230.0]),
        estimated=np.array([229.0, 231.0, 228.0]),
        sigma=np.array([2.0, 3.0, 2.0]),
    )

    figure = _create_voltage_comparison_figure(
        comparison,
        sensor_id=101,
        sigma_multiplier=2.0,
    )

    assert len(figure.data) == 4

    np.testing.assert_array_equal(
        figure.data[0].y,
        [226.0, 229.0, 226.0],
    )
    np.testing.assert_array_equal(
        figure.data[1].y,
        [234.0, 241.0, 234.0],
    )
    np.testing.assert_array_equal(
        figure.data[2].y,
        [230.0, 235.0, 230.0],
    )
    np.testing.assert_array_equal(
        figure.data[3].y,
        [229.0, 231.0, 228.0],
    )

    assert figure.data[1].fill == "tonexty"
    assert figure.data[2].name == "Measured voltage"
    assert figure.data[3].name == "Calculated voltage"
    assert figure.layout.showlegend is True


def test_voltage_comparison_figure_preserves_missing_values():
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1, 2]),
        measured=np.array([230.0, 230.0, 230.0]),
        estimated=np.array([229.0, np.nan, 228.0]),
        sigma=np.array([2.0, np.nan, 2.0]),
    )

    figure = _create_voltage_comparison_figure(
        comparison,
        sensor_id=101,
        sigma_multiplier=2.0,
    )

    np.testing.assert_allclose(
        figure.data[0].y,
        [226.0, np.nan, 226.0],
    )
    np.testing.assert_allclose(
        figure.data[1].y,
        [234.0, np.nan, 234.0],
    )
    np.testing.assert_allclose(
        figure.data[3].y,
        [229.0, np.nan, 228.0],
    )
