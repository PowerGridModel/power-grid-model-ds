# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import math

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from tests.conftest import FancyTestArray

# pylint: disable=missing-function-docstring


def test_exclude_by_id_kwarg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(id=1)
    assert isinstance(array, FancyTestArray)
    assert array.size == 2
    assert_array_equal(array.id, [2, 3])


def test_exclude_by_id_arg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(1)
    assert array.size == 2
    assert_array_equal(array.id, [2, 3])


def test_exclude_by_int(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(test_int=4)
    assert array.size == 2
    assert_array_equal(array.test_int, [3, 0])


def test_exclude_by_float(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(test_float=1.0)
    assert array.size == 2
    assert_array_equal(array.test_float, [4.0, 4.0])


def test_exclude_by_str(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(test_str="c")
    assert array.size == 2
    assert_array_equal(array.test_str, ["a", "d"])


def test_exclude_no_match(fancy_test_array: FancyTestArray):
    assert fancy_test_array.size == 3
    array = fancy_test_array.exclude(test_str="z")
    assert array.size == 3


def test_exclude_multiple_matches(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(test_float=4.0)
    assert array.size == 1
    record = array.record
    assert math.isclose(record.test_float, 1.0)


def test_exclude_no_input(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        fancy_test_array.exclude()


def test_exclude_empty_list_input(fancy_test_array: FancyTestArray):
    assert fancy_test_array.size == 3
    array = fancy_test_array.exclude([])
    assert array.size == 3


def test_exclude_mode_or(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(test_float=1.0, test_str="a", mode_="OR")
    assert 1 == array.size
    assert_array_equal(array.id, [2])


def test_exclude_mask_by_id_kwarg(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(id=1)
    assert isinstance(mask, np.ndarray)
    assert_array_equal(mask, [False, True, True])


def test_exclude_mask_by_id_arg(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(1)
    assert_array_equal(mask, [False, True, True])


def test_exclude_mask_by_int(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_int=4)
    assert_array_equal(mask, [True, True, False])


def test_exclude_mask_by_float(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_float=1.0)
    assert_array_equal(mask, [True, True, False])


def test_exclude_mask_by_str(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_str="c")
    assert_array_equal(mask, [True, False, True])


def test_exclude_mask_no_match(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_str="z")
    assert_array_equal(mask, [True, True, True])


def test_exclude_mask_multiple_matches(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_float=4.0)
    assert_array_equal(mask, [False, False, True])


def test_exclude_mask_no_input(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        fancy_test_array.exclude_mask()


def test_exclude_mask_empty_list_input(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask([])
    assert_array_equal(mask, [True, True, True])


def test_exclude_mask_mode_or(fancy_test_array: FancyTestArray):
    mask = fancy_test_array.exclude_mask(test_float=1.0, test_str="a", mode_="OR")
    assert_array_equal(mask, [False, True, False])


def test_exclude_kwarg_set_input(fancy_test_array: FancyTestArray):
    array = fancy_test_array.exclude(id={1})
    assert isinstance(array, FancyTestArray)
    assert array.size == 2
    assert 1 not in array.id
