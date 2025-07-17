# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from copy import copy

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from numpy.typing import NDArray

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.pgm_arrays import LineArray, TransformerArray
from power_grid_model_ds._core.model.constants import EMPTY_ID, empty
from power_grid_model_ds._core.utils.misc import array_equal_with_nan
from tests.conftest import FancyTestArray
from tests.fixtures.arrays import ExtendedLineArray, FancyTestArray3

# pylint: disable=missing-function-docstring


class _DefaultStrLengthArray(FancyArray):
    test_str: NDArray[np.str_]


class _CustomStrLengthArray(FancyArray):
    test_str: NDArray[np.str_]
    _str_lengths = {"test_str": 100}


class _InheritedStrLengthArray(_CustomStrLengthArray):
    extra_string: NDArray[np.str_]
    _str_lengths = {"extra_string": 100}


def test_get_non_existing_attribute(fancy_test_array: FancyTestArray):
    with pytest.raises(AttributeError):
        # pylint: disable=pointless-statement
        fancy_test_array.non_existing_attribute  # noqa


def test_for_loop(fancy_test_array: FancyTestArray):
    for row in fancy_test_array:
        assert row in fancy_test_array
        assert isinstance(row, FancyTestArray)


def test_setattr(fancy_test_array: FancyTestArray):
    assert_array_equal(fancy_test_array.id, [1, 2, 3])
    fancy_test_array.id = [9, 9, 9]

    assert_array_equal(fancy_test_array.id, [9, 9, 9])
    assert_array_equal(fancy_test_array.data["id"], [9, 9, 9])


def test_prevent_delete_numpy_attribute(fancy_test_array: FancyTestArray):
    with pytest.raises(AttributeError):
        del fancy_test_array.size  # 'size' is a numpy attribute


def test_getitem_array_one_column(fancy_test_array: FancyTestArray):
    assert_array_equal(fancy_test_array["id"], [1, 2, 3])


def test_getitem_array_multiple_columns(fancy_test_array: FancyTestArray):
    columns = ["id", "test_int", "test_float"]
    assert fancy_test_array.data[columns].tolist() == fancy_test_array[columns].tolist()
    assert_array_equal(fancy_test_array[columns].dtype.names, ("id", "test_int", "test_float"))


def test_getitem_unique_multiple_columns(fancy_test_array: FancyTestArray):
    columns = ["id", "test_int", "test_float"]
    assert np.array_equal(np.unique(fancy_test_array[columns]), fancy_test_array[columns])


def test_getitem_array_slice(fancy_test_array: FancyTestArray):
    assert fancy_test_array.data[0:2].tolist() == fancy_test_array[0:2].tolist()


def test_getitem_with_array_mask(fancy_test_array: FancyTestArray):
    mask = np.array([True, False, True])
    assert isinstance(fancy_test_array[mask], FancyArray)
    assert np.array_equal(fancy_test_array.data[mask], fancy_test_array[mask].data)


def test_getitem_with_tuple_mask(fancy_test_array: FancyTestArray):
    mask = (True, False, True)
    assert isinstance(fancy_test_array[mask], FancyArray)
    assert np.array_equal(fancy_test_array.data[mask], fancy_test_array[mask].data)


def test_getitem_with_list_mask(fancy_test_array: FancyTestArray):
    mask = [True, False, True]
    assert isinstance(fancy_test_array[mask], FancyArray)
    assert np.array_equal(fancy_test_array.data[mask], fancy_test_array[mask].data)


def test_getitem_with_empty_list_mask():
    array = FancyTestArray()
    mask = []
    assert isinstance(array[mask], FancyArray)
    assert np.array_equal(array.data[mask], array[mask].data)


def test_setitem_with_index(fancy_test_array: FancyTestArray):
    fancy_test_array[0] = (9, 9, 9, 9, 9)
    assert [9, 2, 3] == fancy_test_array.id.tolist()


def test_setitem_with_mask(fancy_test_array: FancyTestArray):
    mask = np.array([True, False, True])
    fancy_test_array[mask] = (9, 9, 9, 9, 9)
    assert [9, 2, 9] == fancy_test_array.id.tolist()


def test_setitem_as_fancy_array_with_mask(fancy_test_array: FancyTestArray):
    mask = np.array([True, False, True])
    fancy_test_array[mask] = FancyTestArray.zeros(2)
    assert_array_equal([EMPTY_ID, 2, EMPTY_ID], fancy_test_array.id)


def test_setitem_as_fancy_array_with_mask_too_large(fancy_test_array: FancyTestArray):
    mask = np.array([True, False, True])
    with pytest.raises(ValueError):
        fancy_test_array[mask] = FancyTestArray.zeros(3)


def test_set_non_existing_field(fancy_test_array: FancyTestArray):
    with pytest.raises(AttributeError):
        fancy_test_array.non_existing_field = 123


def test_set_callable(fancy_test_array: FancyTestArray):
    with pytest.raises(AttributeError):
        fancy_test_array.filter = 123


def test_contains(fancy_test_array: FancyTestArray):
    assert fancy_test_array[0] in fancy_test_array


def test_non_existing_method(fancy_test_array: FancyTestArray):
    with pytest.raises(AttributeError):
        # pylint: disable=no-member
        fancy_test_array.non_existing_method()


def test_array_equal(fancy_test_array: FancyTestArray):
    assert fp.array_equal(fancy_test_array, fancy_test_array.copy())


def test_array_not_equal(fancy_test_array: FancyTestArray):
    different_array = fancy_test_array.copy()
    different_array.test_int = 99
    assert not fp.array_equal(fancy_test_array, different_array)


def test_nan_array_equal():
    array1 = FancyTestArray.empty(1)
    array2 = FancyTestArray.empty(1)
    assert fp.array_equal(array1, array2)


def test_nan_array_equal_without_equal_nan():
    array1 = FancyTestArray.empty(1)
    array2 = FancyTestArray.empty(1)
    assert not fp.array_equal(array1, array2, equal_nan=False)


def test_nan_ndarray3_equal():
    array1 = FancyTestArray3.empty(10)
    array2 = FancyTestArray3.empty(10)
    assert fp.array_equal(array1, array2)


def test_nan_ndarray3_equal_without_equal_nan():
    array1 = FancyTestArray3.empty(10)
    array2 = FancyTestArray3.empty(10)
    assert not fp.array_equal(array1, array2, equal_nan=False)


def test_is_empty_float():
    array = FancyTestArray.zeros(2)
    array.test_float = [np.nan, 123]
    assert_array_equal(array.is_empty("test_float"), [True, False])


def test_is_empty_integer():
    array = FancyTestArray.zeros(2)
    array.test_int = [empty(np.int64), 123]
    assert_array_equal(array.is_empty("test_int"), [True, False])


def test_is_empty_string():
    array = FancyTestArray.zeros(2)
    array.test_str = ["", "HELLO"]
    assert_array_equal(array.is_empty("test_str"), [True, False])


def test_is_empty_bool():
    array = FancyTestArray.zeros(2)
    array.test_bool = [False, True]
    assert_array_equal(array.is_empty("test_bool"), [True, False])


def test_unique(fancy_test_array: FancyTestArray):
    duplicate_array = fp.concatenate(fancy_test_array, fancy_test_array)
    unique_array = fp.unique(duplicate_array)
    assert fp.array_equal(unique_array, fancy_test_array)


def test_unique_with_nan_values(fancy_test_array: FancyTestArray):
    fancy_test_array.test_float = np.nan
    duplicate_array = fp.concatenate(fancy_test_array, fancy_test_array)
    with pytest.raises(NotImplementedError):
        fp.unique(duplicate_array)


def test_unique_return_inverse(fancy_test_array: FancyTestArray):
    duplicate_array = fp.concatenate(fancy_test_array, fancy_test_array)
    unique_array, inverse = fp.unique(duplicate_array, return_inverse=True)
    assert fp.array_equal(unique_array, fancy_test_array)
    assert_array_equal(inverse, [0, 1, 2, 0, 1, 2])


def test_unique_return_counts_and_inverse(fancy_test_array: FancyTestArray):
    duplicate_array = fp.concatenate(fancy_test_array, fancy_test_array)
    unique_array, inverse, counts = fp.unique(duplicate_array, return_counts=True, return_inverse=True)
    assert fp.array_equal(unique_array, fancy_test_array)
    assert_array_equal(counts, [2, 2, 2])
    assert_array_equal(inverse, [0, 1, 2, 0, 1, 2])


def test_sort(fancy_test_array: FancyTestArray):
    assert_array_equal(fancy_test_array.test_float, [4.0, 4.0, 1.0])
    fancy_test_array.sort(order="test_float")
    assert_array_equal(fancy_test_array.test_float, [1.0, 4.0, 4.0])


def test_copy_function(fancy_test_array: FancyTestArray):
    array_copy = copy(fancy_test_array)
    array_copy.test_int = 123
    assert not id(fancy_test_array) == id(array_copy)
    assert not fancy_test_array.test_int[0] == array_copy.test_int[0]


def test_copy_method(fancy_test_array: FancyTestArray):
    array_copy = fancy_test_array.copy()
    array_copy.test_int = 123
    assert not id(fancy_test_array.data) == id(array_copy.data)
    assert not fancy_test_array.test_int[0] == array_copy.test_int[0]  # type: ignore


def test_prevent_np_unique_on_fancy_array(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        np.unique(fancy_test_array)


def test_prevent_np_sort_on_fancy_array(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        np.sort(fancy_test_array)


def test_string_column_with_long_value():
    array = _DefaultStrLengthArray(test_str=["a" * 100])
    # Test that the string is truncated to _DEFAULT_STRING_LENGTH
    assert_array_equal(array.test_str, ["a" * 50])


def test_string_column_with_long_value_and_custom_string_length():
    array = _CustomStrLengthArray(test_str=["a" * 100])
    assert_array_equal(array.test_str, ["a" * 100])


def test_string_inherit_string_length():
    array = _InheritedStrLengthArray(test_str=["a" * 100], extra_string=["b" * 100])
    assert_array_equal(array.test_str, ["a" * 100])
    assert_array_equal(array.extra_string, ["b" * 100])


def test_shuffle_array(fancy_test_array: FancyTestArray):
    rng = np.random.default_rng(0)
    rng.shuffle(fancy_test_array.data)
    assert_array_equal(fancy_test_array.id, [3, 1, 2])


def test_overflow_value():
    transformer = TransformerArray.empty(1)
    with pytest.raises(OverflowError):
        transformer.tap_min = -167
    assert transformer.tap_min == -128


def test_from_extended_array():
    extended_array = ExtendedLineArray.empty(3)
    extended_array.id = [1, 2, 3]
    extended_array.from_node = [4, 5, 6]
    extended_array.to_node = [7, 8, 9]
    extended_array.from_status = [1, 0, 1]
    extended_array.from_status = [0, 1, 0]

    array = LineArray.from_extended(extended_array)
    assert not isinstance(array, ExtendedLineArray)
    array_equal_with_nan(array.data, extended_array[array.columns])
