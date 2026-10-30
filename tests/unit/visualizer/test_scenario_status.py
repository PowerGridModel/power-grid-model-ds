# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for batch state-estimation scenario status."""

from types import SimpleNamespace

import pytest

from power_grid_model_ds._core.visualizer.scenario_status import (
    CalculationStatus,
    scenario_status_from_batch_error,
)


def test_status_unknown_without_calculation_context():
    status = scenario_status_from_batch_error(None)

    assert status.status_for(0) == CalculationStatus.UNKNOWN


def test_all_scenarios_succeeded_without_batch_error():
    status = scenario_status_from_batch_error(None, scenario_count=3)

    assert status.status_for(0) == CalculationStatus.SUCCEEDED
    assert status.status_for(1) == CalculationStatus.SUCCEEDED
    assert status.status_for(2) == CalculationStatus.SUCCEEDED
    assert status.status_for(3) == CalculationStatus.UNKNOWN


def test_partial_batch_failure():
    batch_error = SimpleNamespace(
        failed_scenarios=[1, 3],
        succeeded_scenarios=[0, 2],
        error_messages=["Scenario 1 failed", "Scenario 3 failed"],
    )

    status = scenario_status_from_batch_error(
        batch_error,
        scenario_count=4,
    )

    assert status.status_for(0) == CalculationStatus.SUCCEEDED
    assert status.status_for(1) == CalculationStatus.FAILED
    assert status.status_for(2) == CalculationStatus.SUCCEEDED
    assert status.status_for(3) == CalculationStatus.FAILED
    assert status.error_messages == (
        "Scenario 1 failed",
        "Scenario 3 failed",
    )
    assert status.error_for(0) is None
    assert status.error_for(1) == "Scenario 1 failed"
    assert status.error_for(2) is None
    assert status.error_for(3) == "Scenario 3 failed"


def test_overlapping_scenario_status_rejected():
    batch_error = SimpleNamespace(
        failed_scenarios=[1],
        succeeded_scenarios=[0, 1],
        error_messages=["Failure"],
    )

    with pytest.raises(ValueError, match="both successful and failed"):
        scenario_status_from_batch_error(batch_error, scenario_count=2)


def test_out_of_range_scenario_rejected():
    batch_error = SimpleNamespace(
        failed_scenarios=[5],
        succeeded_scenarios=[0],
        error_messages=["Failure"],
    )

    with pytest.raises(ValueError, match="invalid index"):
        scenario_status_from_batch_error(batch_error, scenario_count=2)
