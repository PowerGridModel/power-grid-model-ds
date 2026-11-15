# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state


@pytest.fixture(autouse=True)
def reset_server_state() -> None:
    """Reset module-level _state to a clean _AppState before every test."""
    server_state._state = server_state._AppState()


def test_server_state():
    assert server_state._state.grid is None

    test_grid_data = Grid.empty()
    update_data = {
        ComponentType.sym_load: initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    }
    output_data = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))
    }

    server_state.set_app_state(test_grid_data, update_data=update_data, output_data=output_data)

    assert server_state.get_grid() is test_grid_data
    assert server_state._state.update_data is update_data
    assert server_state._state.output_data is output_data


def test_get_grid_uninitialized():
    assert server_state._state.grid is None

    server_state.set_app_state(None)

    with pytest.raises(RuntimeError, match="Grid state not initialized"):
        server_state.get_grid()


def test_set_app_state_accepts_missing_datasets():
    grid = Grid.empty()

    server_state.set_app_state(grid)

    assert server_state.get_grid() is grid
    assert server_state.get_update_data() is None
    assert server_state.get_output_data() is None


def test_set_app_state_accepts_missing_components():
    grid = Grid.empty()
    update_data = {}
    output_data = {}

    server_state.set_app_state(grid, update_data, output_data)

    assert server_state.get_update_data() is update_data
    assert server_state.get_output_data() is output_data


def test_set_app_state_accepts_single_dataset():
    grid = Grid.empty()
    output_data = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, 2)
    }

    server_state.set_app_state(grid, output_data=output_data)

    assert server_state.get_output_data() is output_data


def test_set_app_state_rejects_mismatched_scenario_counts():
    update_data = {
        ComponentType.sym_load: initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    }
    output_data = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (3, 1))
    }

    with pytest.raises(ValueError, match="same scenario count"):
        server_state.set_app_state(Grid.empty(), update_data, output_data)


def test_set_app_state_rejects_invalid_dimensions():
    output_data = {
        ComponentType.node: np.zeros(
            (2, 1, 1),
            dtype=[("id", np.int32), ("u", np.float64)],
        )
    }

    with pytest.raises(ValueError, match="1D or 2D"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_rejects_columnar_data():
    output_data = {
        ComponentType.node: {
            "id": np.array([[1], [1]]),
            "u": np.array([[230.0], [231.0]]),
        }
    }

    with pytest.raises(NotImplementedError, match="columnar"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_rejects_missing_id():
    output_data = {
        ComponentType.node: np.array(
            [[(230.0,)], [(231.0,)]],
            dtype=[("u", np.float64)],
        )
    }

    with pytest.raises(NotImplementedError, match="requires an 'id' field"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_accepts_node_output_without_voltage():
    output_data = {
        ComponentType.node: np.array(
            [[(1, 400.0)], [(1, 410.0)]],
            dtype=[("id", np.int32), ("u_rated", np.float64)],
        )
    }

    server_state.set_app_state(Grid.empty(), output_data=output_data)

    assert server_state.get_output_data() is output_data


def test_set_app_state_rejects_inconsistent_component_batch_sizes():
    output_data = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1)),
        ComponentType.line: initialize_array(DatasetType.sym_output, ComponentType.line, (3, 1)),
    }

    with pytest.raises(ValueError, match="inconsistent or invalid dataset dimensions"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_preserves_previous_state_after_validation_failure():
    original_grid = Grid.empty()
    original_output = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))
    }
    server_state.set_app_state(original_grid, output_data=original_output)

    invalid_output = {
        ComponentType.node: np.array(
            [[(230.0,)]],
            dtype=[("u", np.float64)],
        )
    }

    with pytest.raises(NotImplementedError, match="requires an 'id' field"):
        server_state.set_app_state(Grid.empty(), output_data=invalid_output)

    assert server_state.get_grid() is original_grid
    assert server_state.get_output_data() is original_output
