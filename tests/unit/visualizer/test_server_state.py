# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state


@pytest.fixture(autouse=True)
def reset_server_state() -> None:
    """Reset module-level _state to a clean _AppState before every test."""
    server_state._state = server_state._AppState()


def test_server_state():
    assert server_state._state.grid is None

    test_grid_data = Grid.empty()
    update_data = {"node": np.array([[1, 2], [3, 4]])}
    output_data = {"node": np.array([[5, 6], [7, 8]])}
    server_state.set_app_state(test_grid_data, update_data=update_data, output_data=output_data)
    assert server_state.get_grid() is test_grid_data
    assert server_state._state.update_data is update_data
    assert server_state._state.output_data is output_data


def test_get_grid_uninitialized():
    assert server_state._state.grid is None

    server_state.set_app_state(None)

    with pytest.raises(RuntimeError, match="Grid state not initialized"):
        server_state.get_grid()


def test_reject_mismatched_update_and_output_scenario_counts():
    grid = Grid.empty()
    with pytest.raises(ValueError, match="same scenario count"):
        server_state.set_app_state(
            grid,
            update_data={"sensor": np.zeros((2, 1))},
            output_data={"node": np.zeros((3, 1))},
        )
    assert server_state._state.grid is None
    assert server_state._state.update_data is None
    assert server_state._state.output_data is None


def test_reject_inconsistent_component_scenario_counts():
    with pytest.raises(ValueError, match="same scenario count"):
        server_state.set_app_state(
            Grid.empty(),
            output_data={"node": np.zeros((3, 1)), "source": np.zeros((2, 1))},
        )
    assert server_state._state.grid is None


def test_single_dataset_does_not_require_the_other_dataset():
    grid = Grid.empty()
    output_data = {"node": np.zeros((3, 1))}
    server_state.set_app_state(grid, output_data=output_data)
    assert server_state.get_grid() is grid
    assert server_state.get_output_data() is output_data
    assert server_state.get_update_data() is None


def test_invalid_scenario_counts_preserve_existing_state():
    """A rejected dataset must not replace previously initialized state."""
    original_grid = Grid.empty()
    original_output = {"node": np.zeros((2, 1))}

    server_state.set_app_state(original_grid, output_data=original_output)

    with pytest.raises(ValueError, match="same scenario count"):
        server_state.set_app_state(
            Grid.empty(),
            update_data={"sensor": np.zeros((2, 1))},
            output_data={"node": np.zeros((3, 1))},
        )

    assert server_state.get_grid() is original_grid
    assert server_state.get_output_data() is original_output
    assert server_state.get_update_data() is None
