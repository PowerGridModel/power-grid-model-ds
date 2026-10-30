# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for scenario-status propagation through the public visualizer API."""

from unittest.mock import MagicMock, patch

from power_grid_model_ds._core.visualizer.scenario_status import ScenarioStatus
from power_grid_model_ds.visualizer import visualize


def test_visualize_forwards_scenario_status():
    grid = MagicMock()
    status = ScenarioStatus(
        succeeded_scenarios=frozenset({0}),
        failed_scenarios=frozenset({1}),
    )

    with (
        patch("power_grid_model_ds.visualizer.server_state.set_app_state") as set_state,
        patch("power_grid_model_ds.visualizer.get_app_layout"),
        patch("power_grid_model_ds.visualizer.Dash") as dash_class,
    ):
        visualize(grid, scenario_status=status)

    set_state.assert_called_once_with(
        grid,
        None,
        None,
        scenario_status=status,
    )
    dash_class.return_value.run.assert_called_once_with(
        debug=False,
        port=8050,
        threaded=False,
    )


def test_visualize_without_scenario_status():
    grid = MagicMock()

    with (
        patch("power_grid_model_ds.visualizer.server_state.set_app_state") as set_state,
        patch("power_grid_model_ds.visualizer.get_app_layout"),
        patch("power_grid_model_ds.visualizer.Dash"),
    ):
        visualize(grid)

    set_state.assert_called_once_with(
        grid,
        None,
        None,
        scenario_status=None,
    )
