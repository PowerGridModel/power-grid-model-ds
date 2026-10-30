# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Represent state-estimation calculation status for batch scenarios."""

from dataclasses import dataclass
from enum import StrEnum

from power_grid_model.errors import PowerGridBatchError


class CalculationStatus(StrEnum):
    """Calculation outcome for one scenario."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ScenarioStatus:
    """Scenario indices and their reported calculation outcomes."""

    succeeded_scenarios: frozenset[int]
    failed_scenarios: frozenset[int]
    error_messages: tuple[str, ...] = ()
    failed_scenario_messages: tuple[tuple[int, str], ...] = ()

    def status_for(self, scenario: int) -> CalculationStatus:
        """Return the reported status for a scenario index."""
        if scenario in self.failed_scenarios:
            return CalculationStatus.FAILED

        if scenario in self.succeeded_scenarios:
            return CalculationStatus.SUCCEEDED

        return CalculationStatus.UNKNOWN

    def error_for(self, scenario: int) -> str | None:
        """Return the solver error associated with a failed scenario."""
        for failed_index, message in self.failed_scenario_messages:
            if failed_index == scenario:
                return message

        return None


def scenario_status_from_batch_error(
    batch_error: PowerGridBatchError | None,
    *,
    scenario_count: int | None = None,
) -> ScenarioStatus:
    """Convert Power Grid Model batch-error information to scenario status.

    When no batch error is present, scenario status is only marked as
    successful if the caller explicitly supplies the scenario count.
    """
    if scenario_count is not None and scenario_count < 0:
        raise ValueError("Scenario count must not be negative.")

    if batch_error is None:
        succeeded = (
            frozenset(range(scenario_count))
            if scenario_count is not None
            else frozenset()
        )
        return ScenarioStatus(
            succeeded_scenarios=succeeded,
            failed_scenarios=frozenset(),
        )

    failed_indices = tuple(
        int(index) for index in batch_error.failed_scenarios
    )
    failed = frozenset(failed_indices)

    error_messages = tuple(
        str(message) for message in batch_error.error_messages
    )

    if len(failed_indices) != len(error_messages):
        raise ValueError(
            "Each failed scenario must have a corresponding error message."
        )

    if len(failed_indices) != len(failed):
        raise ValueError("Duplicate failed scenario indices are not allowed.")

    succeeded = frozenset(
        int(index) for index in batch_error.succeeded_scenarios
    )

    if failed & succeeded:
        raise ValueError(
            "A scenario cannot be both successful and failed."
        )

    if scenario_count is not None:
        valid_indices = set(range(scenario_count))
        if not (failed | succeeded) <= valid_indices:
            raise ValueError("Scenario status contains an invalid index.")

    return ScenarioStatus(
        succeeded_scenarios=succeeded,
        failed_scenarios=failed,
        error_messages=error_messages,
        failed_scenario_messages=tuple(
            zip(failed_indices, error_messages, strict=True)
        ),
    )
