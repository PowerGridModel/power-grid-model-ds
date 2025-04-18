# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import math

import pytest

from power_grid_model_ds._core.model.arrays.base.errors import MultipleRecordsReturned, RecordDoesNotExist
from tests.conftest import FancyTestArray

# pylint: disable=missing-function-docstring


def test_get_by_id_kwarg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.get(id=1)
    assert isinstance(array, FancyTestArray)
    assert array.id == 1


def test_get_by_id_arg(fancy_test_array: FancyTestArray):
    array = fancy_test_array.get(1)
    assert isinstance(array, FancyTestArray)
    assert array.id == 1


def test_get_by_int(fancy_test_array: FancyTestArray):
    array = fancy_test_array.get(test_int=4)
    assert array.test_int == 4


def test_get_by_float(fancy_test_array: FancyTestArray):
    record = fancy_test_array.get(test_float=1.0).record
    assert math.isclose(record.test_float, 1.0)


def test_get_by_str(fancy_test_array: FancyTestArray):
    array = fancy_test_array.get(test_str="c")
    assert array.test_str == "c"


def test_get_no_match(fancy_test_array: FancyTestArray):
    with pytest.raises(RecordDoesNotExist):
        fancy_test_array.get(99)


def test_get_multiple_matches(fancy_test_array: FancyTestArray):
    with pytest.raises(MultipleRecordsReturned):
        fancy_test_array.get(test_float=4.0)


def test_get_no_input(fancy_test_array: FancyTestArray):
    with pytest.raises(TypeError):
        fancy_test_array.get()


def test_get_kwarg_set_input(fancy_test_array: FancyTestArray):
    array = fancy_test_array.get(id={1})
    assert isinstance(array, FancyTestArray)
    assert array.size == 1
    assert array.id == 1
