# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for scenario-status storage in the visualizer server state."""

import pytest

from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.scenario_status import ScenarioStatus


@pytest.fixture(autouse=True)
def reset_scenario_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use isolated application state for each test."""
    monkeypatch.setattr(server_state, "_state", server_state._AppState())


def test_scenario_status_is_stored():
    status = ScenarioStatus(
        succeeded_scenarios=frozenset({0, 2}),
        failed_scenarios=frozenset({1}),
    )

    server_state.set_app_state(
        grid=None,
        scenario_status=status,
    )

    assert server_state.get_scenario_status() == status


def test_scenario_status_is_optional():
    server_state.set_app_state(grid=None)

    assert server_state.get_scenario_status() is None


def test_new_app_state_clears_previous_scenario_status():
    status = ScenarioStatus(
        succeeded_scenarios=frozenset({0}),
        failed_scenarios=frozenset({1}),
    )

    server_state.set_app_state(
        grid=None,
        scenario_status=status,
    )

    server_state.set_app_state(grid=None)

    assert server_state.get_scenario_status() is None
