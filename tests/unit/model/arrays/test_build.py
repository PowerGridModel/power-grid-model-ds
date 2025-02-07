# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from numpy.typing import NDArray

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays import AsymVoltageSensorArray, SymPowerSensorArray
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.base.errors import ArrayDefinitionError
from power_grid_model_ds._core.model.constants import EMPTY_ID
from tests.fixtures.arrays import DefaultedFancyTestArray, FancyTestArray

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code


class InvalidArray(FancyArray):
    id: NDArray[np.int64]
    data: NDArray[np.int64]
    size: NDArray[np.int64]


class ExtendedFancyTestArray(FancyTestArray):
    _defaults = {"test_float2": np.nan, "test_float3": 42.0}

    test_float2: NDArray[np.float64]
    test_float3: NDArray[np.float64]


class ExtendedFancyTestArrayNoDefaults(FancyTestArray):
    test_float2: NDArray[np.float64]
    test_float3: NDArray[np.float64]


class ChildArray(DefaultedFancyTestArray):
    _defaults = {"test_float4": 42.0}

    test_float4: NDArray[np.float64]


class SizedDTypesArray(FancyArray):
    test_float16: NDArray[np.float16]
    test_float32: NDArray[np.float32]
    test_float64: NDArray[np.float64]

    test_int8: NDArray[np.int8]
    test_int16: NDArray[np.int16]
    test_int32: NDArray[np.int32]
    test_int64: NDArray[np.int64]


def test_build_without_array_definition():
    with pytest.raises(ArrayDefinitionError):
        FancyArray()


def test_build_without_args_or_kwargs():
    array = FancyTestArray()
    assert_array_equal(array.id, [])
    assert 0 == array.size


def test_build_from_kwargs():
    array = FancyTestArray(
        id=[1, 2, 3],
        test_int=[3, 0, 4],
        test_float=[4.0, 4.0, 1.0],
        test_str=["a", "c", "d"],
        test_bool=[True, False, True],
    )
    assert array.size == 3
    assert_array_equal(array.id, [1, 2, 3])
    assert_array_equal(array.test_int, [3, 0, 4])
    assert_array_equal(array.test_float, [4.0, 4.0, 1.0])
    assert_array_equal(array.test_str, ["a", "c", "d"])
    assert_array_equal(array.test_bool, [True, False, True])


def test_build_from_kwargs_with_missing_input_fields():
    with pytest.raises(ValueError):
        FancyTestArray(
            id=[1, 2, 3],
            test_int=[3, 0, 4],
            test_float=[4.0, 4.0, 1.0],
            # test_str = missing
            # test_bool = missing
        )


def test_build_from_kwargs_with_different_input_lengths():
    with pytest.raises(ValueError):
        FancyTestArray(
            id=[1, 2, 3],
            test_int=[3, 0, 4],
            test_float=[4.0, 4.0, 1.0],
            test_str=["a", "c", "d"],
            test_bool=[True, False, True, True],  # extra element
        )


def test_build_from_args(fancy_test_array):
    array = FancyTestArray(
        (1, 3, 4.0, "a", True),
        (2, 0, 4.0, "c", False),
        (3, 4, 1.0, "d", True),
    )
    assert fp.array_equal(array, fancy_test_array)


def test_build_from_invalid_args():
    with pytest.raises(TypeError):
        FancyTestArray(1)


def test_build_from_numpy_array(fancy_test_array):
    array = FancyTestArray(fancy_test_array.data)
    assert fp.array_equal(array, fancy_test_array)


def test_build_from_numpy_array_with_data_kwarg(fancy_test_array):
    array = FancyTestArray(data=fancy_test_array.data)
    assert fp.array_equal(array, fancy_test_array)


def test_build_from_numpy_2d_shape_2_4():
    numpy_array = np.array([[1, 2, 3, 4, 5], [9, 9, 9, 9, 9]])
    assert (2, 5) == numpy_array.shape
    array = FancyTestArray(numpy_array)
    assert_array_equal([2, 9], array.test_int)
    assert 2 == array.size


def test_build_from_numpy_2d_shape_4_2():
    numpy_array = np.array([[15, 9], [2, 9], [3, 9], [4, 9], [7, 9]])
    assert (5, 2) == numpy_array.shape
    array = FancyTestArray(numpy_array)
    assert_array_equal([2, 9], array.test_int)
    assert 2 == array.size


def test_array_invalid_columns_before_initialization():
    with pytest.raises(ArrayDefinitionError):
        InvalidArray(id=[1, 2, 3, 4, 5])


def test_some_zeros():
    array = FancyTestArray.zeros(3)
    assert 3 == array.size
    assert_array_equal([np.iinfo(np.int32).min] * 3, array.id)
    assert_array_equal([0, 0, 0], array.test_int)
    assert 3 == array.size
    assert 3 == len(array)
    assert 3 == len(array.data)
    assert 3 == len(array.id)
    assert 3 == len(array.test_int)
    assert 3 == len(array.test_float)


def test_many_zeros():
    array = FancyTestArray.zeros(int(1e6))
    assert int(1e6) == array.size
    assert int(1e6) == len(array)
    assert int(1e6) == len(array.data)
    assert int(1e6) == len(array.id)
    assert int(1e6) == len(array.test_int)
    assert int(1e6) == len(array.test_float)


def test_empty():
    array = FancyTestArray.empty(3)
    assert 3 == array.size
    assert_array_equal([EMPTY_ID, EMPTY_ID, EMPTY_ID], array.id)
    min_int64 = np.iinfo(np.int64).min
    assert_array_equal([min_int64] * 3, array.test_int)


def test_empty_with_sized_dtypes():
    array = SizedDTypesArray.empty(1)

    assert_array_equal([np.iinfo(np.int8).min], array.test_int8)
    assert_array_equal([np.iinfo(np.int16).min], array.test_int16)
    assert_array_equal([np.iinfo(np.int32).min], array.test_int32)
    assert_array_equal([np.iinfo(np.int64).min], array.test_int64)

    assert_array_equal([np.nan], array.test_float16)
    assert_array_equal([np.nan], array.test_float32)
    assert_array_equal([np.nan], array.test_float64)


def test_empty_with_defaults():
    array = DefaultedFancyTestArray.empty(3)
    assert 3 == array.size
    assert_array_equal([-1, -1, -1], array.id)
    assert_array_equal([4, 4, 4], array.test_int)
    assert_array_equal([4.5, 4.5, 4.5], array.test_float)
    assert_array_equal(["DEFAULT", "DEFAULT", "DEFAULT"], array.test_str)


def test_from_structured_subarray_with_defaults(fancy_test_array):
    array = ExtendedFancyTestArray(fancy_test_array.data)
    assert 3 == array.size
    assert all(np.isnan(array.test_float2))
    assert_array_equal([42.0, 42.0, 42.0], array.test_float3)


def test_from_structured_subarray_no_defaults(fancy_test_array):
    with pytest.raises(ValueError):
        ExtendedFancyTestArrayNoDefaults(fancy_test_array.data)


def test_from_sub_ndarray_with_defaults(fancy_test_array):
    # defaults are not supported when working with unstructured arrays
    sub_ndarray = np.array(fancy_test_array.tolist())
    with pytest.raises(ValueError):
        ExtendedFancyTestArray(sub_ndarray)


def test_from_sub_ndarray_no_defaults(fancy_test_array):
    sub_ndarray = np.array(fancy_test_array.tolist())
    with pytest.raises(ValueError):
        ExtendedFancyTestArrayNoDefaults(sub_ndarray)


def test_initialization_from_args_with_extra_columns():
    data = np.array([1, 2], dtype=[("id", np.int_), ("undefined", np.int_)])
    array = DefaultedFancyTestArray(data)

    assert isinstance(array, DefaultedFancyTestArray)
    assert "undefined" not in array.dtype.names


def test_sensor_array():
    test_len = 2
    # test proper intiliazation of a SensorArray
    pow_sens = SymPowerSensorArray.empty(test_len)
    sym_pow_fields = [
        "measured_object",
        "measured_terminal_type",
        "power_sigma",
        "p_measured",
        "p_sigma",
        "q_measured",
        "q_sigma",
    ]
    for field in sym_pow_fields:
        assert field in pow_sens.dtype.fields

    # test if asymmetric array has NDArray3 fields, i.e. with 3 floats per element (one per phase)
    asym_volt_sens = AsymVoltageSensorArray.empty(test_len)
    nd3_fields = ["u_sigma", "u_measured", "u_angle_measured"]
    for field in nd3_fields:
        assert asym_volt_sens[field].shape == (test_len, 3)


def test_inherit_defaults_from_multiple_parents():
    array = ChildArray.empty(3)
    assert 3 == array.size
    assert_array_equal([-1, -1, -1], array.id)
    assert_array_equal([4, 4, 4], array.test_int)
    assert_array_equal([4.5, 4.5, 4.5], array.test_float)
    assert_array_equal(["DEFAULT", "DEFAULT", "DEFAULT"], array.test_str)
    assert_array_equal([42.0, 42.0, 42.0], array.test_float4)
