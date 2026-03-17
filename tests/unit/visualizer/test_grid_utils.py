# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.grid_utils import (
    dynamic_grid_obj_from_grid,
    extend_grid_dynamically,
    get_attr_data_from_dataset,
)


@pytest.mark.parametrize(
    "dataset_type",
    [DatasetType.input, DatasetType.update, DatasetType.sym_output, DatasetType.sc_output, DatasetType.asym_output],
)
def test_extend_grid_dynamically_with_pgm_dataset(dataset_type):
    extra_dataset = {k: initialize_array(dataset_type, k, (2, 3)) for k in ComponentType}
    DynamicGrid = extend_grid_dynamically(Grid, extra_dataset=extra_dataset)
    dynamic_grid_obj = DynamicGrid.empty()
    for grid_attr in extra_dataset:
        grid_array = getattr(dynamic_grid_obj, grid_attr)
        extra_dataset_dtype_fields = extra_dataset[grid_attr].dtype.fields
        assert extra_dataset_dtype_fields is not None

        for attr in extra_dataset_dtype_fields:
            assert hasattr(grid_array, attr), f"dynamic_grid_obj.'{grid_attr}' should have attribute '{attr}'"

            # Check only dtype[0], skip full dtype. Offsets of PGM-DS are not same as PGM at the moment
            expected_dtype = extra_dataset_dtype_fields[attr][0]
            actual_dtype = grid_array.dtype.fields[attr][0]
            assert actual_dtype == expected_dtype, (
                f"{actual_dtype} != {expected_dtype} for dynamic_grid_obj.'{grid_attr}'.'{attr}'"
            )


@pytest.mark.parametrize(
    "dataset_type",
    [DatasetType.input, DatasetType.update, DatasetType.sym_output, DatasetType.sc_output, DatasetType.asym_output],
)
def test_dynamic_grid_obj_from_grid(dataset_type):
    grid = Grid.empty()
    for attr in grid.__annotations__:
        if isinstance(getattr(grid, attr), FancyArray):
            grid_array = getattr(grid, attr).__class__.empty(2)
            grid_array[:] = 99
            setattr(grid, attr, grid_array)

    extra_dataset = {k: initialize_array(dataset_type, k, (2, 3)) for k in ComponentType}

    DynamicGrid = extend_grid_dynamically(Grid, extra_dataset=extra_dataset)
    new_grid_obj = dynamic_grid_obj_from_grid(DynamicGrid, grid)

    for grid_attr in new_grid_obj.__annotations__:
        grid_array = getattr(grid, grid_attr)
        new_grid_array = getattr(new_grid_obj, grid_attr)

        if not isinstance(grid_array, FancyArray):
            # skip non-array attributes
            continue

        assert new_grid_array.shape == (2,), f"Expected shape (2,) got {new_grid_array.shape}"

        for array_attr in new_grid_array.columns:
            empty_value = empty(new_grid_array[array_attr].dtype)
            if array_attr in grid_array.columns:
                assert np.array_equal(new_grid_array[array_attr], grid_array[array_attr]), (
                    f"new_grid_obj.'{grid_attr}'['{array_attr}'] != grid.'{grid_attr}'['{array_attr}']"
                )
            elif empty_value is np.nan:
                assert np.all(np.isnan(new_grid_array[array_attr])), (
                    f"new_grid_obj.'{grid_attr}'['{array_attr}'] should be initialized to empty value (nan)"
                )
            else:
                assert np.all(new_grid_array[array_attr] == empty_value), (
                    f"new_grid_obj.'{grid_attr}'['{array_attr}'] should be initialized to empty value ({empty_value})"
                )


def test_get_attr_data_from_dataset():
    loads = initialize_array(DatasetType.update, ComponentType.sym_load, (4, 3))
    loads["p_specified"] = [[21, 22, 23], [31, 32, 33], [41, 42, 43], [51, 52, 53]]

    # Normal case with matching pgm_id=12
    loads["id"] = [[11, 12, 13], [11, 12, 13], [11, 12, 13], [11, 12, 13]]
    batch_dataset = {ComponentType.sym_load: loads}
    x_actual, y_actual = get_attr_data_from_dataset(batch_dataset, ComponentType.sym_load, "p_specified", pgm_id=12)
    assert np.array_equal(y_actual, np.array([22, 32, 42, 52]))
    assert np.array_equal(x_actual, np.array([0, 1, 2, 3]))

    # Order changed
    loads["id"] = [[11, 12, 13], [13, 11, 12], [11, 12, 13], [13, 11, 12]]
    x_actual, y_actual = get_attr_data_from_dataset(batch_dataset, ComponentType.sym_load, "p_specified", pgm_id=12)
    assert np.array_equal(y_actual, np.array([22, 33, 42, 53]))
    assert np.array_equal(x_actual, np.array([0, 1, 2, 3]))

    # Missing scenario for pgm_id=12
    loads["id"] = [[11, 12, 13], [14, 15, 16], [11, 12, 13], [14, 15, 16]]
    x_actual, y_actual = get_attr_data_from_dataset(batch_dataset, ComponentType.sym_load, "p_specified", pgm_id=12)
    assert np.array_equal(y_actual, np.array([22, 42]))
    assert np.array_equal(x_actual, np.array([0, 2]))

    # Duplicate pgm_id=12 in a scenario
    loads["id"] = [[11, 12, 13], [11, 12, 12], [11, 12, 13], [11, 12, 13]]
    with pytest.raises(ValueError, match="Erraneous dataset."):
        get_attr_data_from_dataset(batch_dataset, ComponentType.sym_load, "p_specified", pgm_id=12)


def test_get_attr_data_from_dataset_3ph():
    loads = initialize_array(DatasetType.update, ComponentType.asym_load, (4, 3))
    loads["p_specified"] = [
        [[21.1, 21.2, 21.3], [22.1, 22.2, 22.3], [23.1, 23.2, 23.3]],
        [[31.1, 31.2, 31.3], [32.1, 32.2, 32.3], [33.1, 33.2, 33.3]],
        [[41.1, 41.2, 41.3], [42.1, 42.2, 42.3], [43.1, 43.2, 43.3]],
        [[51.1, 51.2, 51.3], [52.1, 52.2, 52.3], [53.1, 53.2, 53.3]],
    ]

    # Normal case with matching pgm_id=12
    loads["id"] = [[11, 12, 13], [11, 12, 13], [11, 12, 13], [11, 12, 13]]
    batch_dataset = {ComponentType.asym_load: loads}
    x_actual, y_actual = get_attr_data_from_dataset(batch_dataset, ComponentType.asym_load, "p_specified", pgm_id=12)
    assert np.array_equal(
        y_actual, np.array([[22.1, 22.2, 22.3], [32.1, 32.2, 32.3], [42.1, 42.2, 42.3], [52.1, 52.2, 52.3]])
    )
    assert np.array_equal(x_actual, np.array([0, 1, 2, 3]))
