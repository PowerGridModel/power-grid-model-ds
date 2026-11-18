# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state


def grid_with_ids(component, ids):
    grid = Grid.empty()
    array = getattr(grid, component.value).__class__.empty(len(ids))
    array.id = np.asarray(ids, dtype=np.int32)
    setattr(grid, component.value, array)
    return grid


@pytest.fixture(autouse=True)
def reset_server_state() -> None:
    server_state._state = server_state._AppState()


def test_server_state():
    grid = grid_with_ids(ComponentType.sym_load, [10])
    update_data = {ComponentType.sym_load: initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))}
    update_data[ComponentType.sym_load]["id"] = 10
    output_data = {ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))}
    output_data[ComponentType.node]["id"] = 20
    node_array = grid.node.__class__.empty(1)
    node_array.id = np.array([20], dtype=np.int32)
    grid.node = node_array
    server_state.set_app_state(grid, update_data, output_data)
    assert server_state.get_grid() is grid
    assert server_state.get_update_data() is update_data
    assert server_state.get_output_data() is output_data


def test_get_grid_uninitialized():
    with pytest.raises(RuntimeError, match="Grid state not initialized"):
        server_state.get_grid()


def test_set_app_state_accepts_missing_datasets():
    grid = Grid.empty()
    server_state.set_app_state(grid)
    assert server_state.get_grid() is grid
    assert server_state.get_update_data() is None
    assert server_state.get_output_data() is None


def test_set_app_state_accepts_missing_components():
    update_data = {}
    output_data = {}
    server_state.set_app_state(Grid.empty(), update_data, output_data)
    assert server_state.get_update_data() is update_data
    assert server_state.get_output_data() is output_data


def test_set_app_state_accepts_single_dataset():
    output_data = {ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, 2)}
    output_data[ComponentType.node]["id"] = [10, 11]
    server_state.set_app_state(grid_with_ids(ComponentType.node, [10, 11]), output_data=output_data)
    assert server_state.get_output_data() is output_data


def test_set_app_state_rejects_mismatched_scenario_counts():
    updates = {ComponentType.sym_load: initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))}
    outputs = {ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (3, 1))}
    with pytest.raises(ValueError, match="same scenario count"):
        server_state.set_app_state(Grid.empty(), updates, outputs)


def test_set_app_state_rejects_invalid_dimensions():
    output_data = {ComponentType.node: np.zeros((2, 1, 1), dtype=[("id", np.int32), ("u", np.float64)])}
    with pytest.raises(ValueError, match="1D or 2D"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_rejects_columnar_data():
    output_data = {ComponentType.node: {"id": np.array([[1], [1]]), "u": np.array([[230.0], [231.0]])}}
    with pytest.raises(NotImplementedError, match="columnar"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_rejects_missing_id():
    output_data = {ComponentType.node: np.array([[(230.0,)], [(231.0,)]], dtype=[("u", np.float64)])}
    with pytest.raises(NotImplementedError, match="requires an 'id' field"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_rejects_inconsistent_component_batch_sizes():
    output_data = {
        ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1)),
        ComponentType.line: initialize_array(DatasetType.sym_output, ComponentType.line, (3, 1)),
    }
    with pytest.raises(ValueError, match="inconsistent or invalid dataset dimensions"):
        server_state.set_app_state(Grid.empty(), output_data=output_data)


def test_set_app_state_preserves_previous_state_after_validation_failure():
    grid = Grid.empty()
    original_output = {ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))}
    original_output[ComponentType.node]["id"] = 10
    grid = grid_with_ids(ComponentType.node, [10])
    server_state.set_app_state(grid, output_data=original_output)
    invalid_output = {ComponentType.node: np.array([[(230.0,)]], dtype=[("u", np.float64)])}
    with pytest.raises(NotImplementedError, match="requires an 'id' field"):
        server_state.set_app_state(Grid.empty(), output_data=invalid_output)
    assert server_state.get_grid() is grid
    assert server_state.get_output_data() is original_output


def test_update_ids_may_be_reordered():
    grid = grid_with_ids(ComponentType.sym_load, [10, 11])
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 2))
    updates["id"] = [[10, 11], [11, 10]]
    server_state.set_app_state(grid, {ComponentType.sym_load: updates})


def test_update_ids_must_exist_in_grid():
    grid = grid_with_ids(ComponentType.sym_load, [10, 11])
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    updates["id"] = [[10], [12]]
    with pytest.raises(ValueError, match="subset of grid IDs"):
        server_state.set_app_state(grid, {ComponentType.sym_load: updates})


def test_output_ids_must_equal_grid_ids():
    grid = grid_with_ids(ComponentType.sym_load, [10, 11])
    outputs = initialize_array(DatasetType.sym_output, ComponentType.sym_load, (2, 2))
    outputs["id"] = [[11, 10], [10, 12]]
    with pytest.raises(ValueError, match="must match grid IDs"):
        server_state.set_app_state(grid, output_data={ComponentType.sym_load: outputs})


def test_update_ids_must_be_unique():
    grid = grid_with_ids(ComponentType.sym_load, [10, 11])
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 2))
    updates["id"] = [[10, 10], [10, 11]]
    with pytest.raises(ValueError, match="duplicate IDs"):
        server_state.set_app_state(grid, {ComponentType.sym_load: updates})


def test_ids_not_compared_when_component_missing_from_one_side():
    grid = grid_with_ids(ComponentType.sym_load, [10])
    node_array = grid.node.__class__.empty(1)
    node_array.id = np.array([20], dtype=np.int32)
    grid.node = node_array
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    outputs = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))
    updates["id"] = 10
    outputs["id"] = 20
    server_state.set_app_state(grid, {ComponentType.sym_load: updates}, {ComponentType.node: outputs})


def test_shared_non_node_component_requires_id():
    """The common dense representation rule applies to every component."""
    outputs = {ComponentType.line: np.zeros((2, 1), dtype=[("p_from", np.float64)])}
    with pytest.raises(NotImplementedError, match="requires an 'id' field"):
        server_state.set_app_state(Grid.empty(), output_data=outputs)


def test_validate_datasets_checks_cross_dataset_counts():
    updates = {ComponentType.sym_load: initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))}
    outputs = {ComponentType.node: initialize_array(DatasetType.sym_output, ComponentType.node, (3, 1))}
    with pytest.raises(ValueError, match="same scenario count"):
        server_state._validate_datasets(Grid.empty(), updates, outputs)


def test_shared_component_ids_allow_sparse_update_subset():
    """Output may contain components that were not updated."""
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    outputs = initialize_array(DatasetType.sym_output, ComponentType.sym_load, (2, 3))

    updates["id"] = [[10], [11]]
    outputs["id"] = [[10, 11, 12], [10, 11, 12]]

    grid = grid_with_ids(ComponentType.sym_load, [10, 11, 12])
    server_state.set_app_state(
        grid,
        {ComponentType.sym_load: updates},
        {ComponentType.sym_load: outputs},
    )


def test_output_ids_can_be_reordered():
    grid = grid_with_ids(ComponentType.sym_load, [10, 11])
    outputs = initialize_array(DatasetType.sym_output, ComponentType.sym_load, (2, 2))
    outputs["id"] = [[11, 10], [10, 11]]
    server_state.set_app_state(grid, output_data={ComponentType.sym_load: outputs})


def test_set_app_state_rejects_input_dataset_as_update():
    grid = grid_with_ids(ComponentType.node, [10])
    nodes = initialize_array(DatasetType.input, ComponentType.node, (2, 1))
    nodes["id"] = 10
    with pytest.raises(ValueError, match="unsupported dataset type"):
        server_state.set_app_state(grid, update_data={ComponentType.node: nodes})


def test_set_app_state_rejects_update_dataset_as_output():
    grid = grid_with_ids(ComponentType.sym_load, [10])
    updates = initialize_array(DatasetType.update, ComponentType.sym_load, (2, 1))
    updates["id"] = 10
    with pytest.raises(ValueError, match="unsupported dataset type"):
        server_state.set_app_state(grid, output_data={ComponentType.sym_load: updates})


def test_set_app_state_rejects_incorrect_output_dtype():
    grid = grid_with_ids(ComponentType.node, [10])
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))
    nodes["id"] = 10
    invalid = nodes[["id", "u"]].copy()
    with pytest.raises(ValueError, match=r"schema|dtype"):
        server_state.set_app_state(grid, output_data={ComponentType.node: invalid})
