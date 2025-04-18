# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import math

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from tests.conftest import FancyTestArray

# pylint: disable=missing-function-docstring


def test_filter_by_id_kwarg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(id=1)
    assert isinstance(array, FancyTestArray)
    assert array.size == 1
    assert array.id == 1


def test_filter_by_id_arg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(1)
    assert array.size == 1
    assert array.id == 1


def test_filter_keeps_original_order():
    original_array = FancyTestArray.zeros(9)
    original_array.id = [1, 3, 2, 4, 5, 6, 7, 8, 16]
    array = original_array.filter(id=[2, 4, 5, 16, 3])
    np.testing.assert_array_equal([3, 2, 4, 5, 16], array.id)


def test_filter_by_int(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_int=4)
    assert array.size == 1
    assert array.test_int == 4


def test_filter_by_float(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_float=1.0)
    assert array.size == 1
    record = array.record
    assert math.isclose(record.test_float, 1.0)


def test_filter_by_str(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_str="c")
    assert array.size == 1
    assert array.test_str == "c"


def test_filter_no_match(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_str="z")
    assert array.size == 0


def test_filter_multiple_matches(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_float=4.0)
    assert array.size == 2
    assert_array_equal(array.test_float, [4.0, 4.0])


def test_filter_no_input(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        fancy_test_array.filter()


def test_filter_empty_list_input(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter([])
    assert array.size == 0


def test_filter_mode_or(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(test_float=1.0, test_str="a", mode_="OR")
    assert 2 == array.size
    assert_array_equal(array.id, [1, 3])


def test_filter_mask_by_id_kwarg(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(id=1)
    assert isinstance(mask, np.ndarray)
    assert_array_equal(mask, [True, False, False])


def test_filter_mask_by_id_arg(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(1)
    assert_array_equal(mask, [True, False, False])


def test_filter_mask_by_int(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(test_int=4)
    assert_array_equal(mask, [False, False, True])


def test_filter_mask_by_float(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(test_float=1.0)
    assert_array_equal(mask, [False, False, True])


def test_filter_mask_by_str(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(test_str="c")
    assert_array_equal(mask, [False, True, False])


def test_filter_mask_no_match(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(test_str="z")
    assert_array_equal(mask, [False, False, False])


def test_filter_mask_multiple_matches(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask(test_float=4.0)
    assert_array_equal(mask, [True, True, False])


def test_filter_mask_no_input(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        fancy_test_array.filter_mask()


def test_filter_mask_empty_list_input(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.filter_mask([])
    assert_array_equal(mask, [False, False, False])


def test_filter_mask_mode_or(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter_mask(test_float=1.0, test_str="a", mode_="OR")
    assert_array_equal(array, [True, False, True])


def test_filter_kwarg_by_set_input(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter(id={1})
    assert isinstance(array, FancyTestArray)
    assert array.size == 1
    assert array.id == 1


def test_filter_arg_by_set_input(fancy_test_array: FancyTestArray):
    array = fancy_test_array.filter({1, 2})
    assert isinstance(array, FancyTestArray)
    assert array.size == 2
    assert_array_equal(array.id, [1, 2])
