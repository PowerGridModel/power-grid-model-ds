# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from power_grid_model_ds._core.utils.misc import array_equal_with_nan, is_sequence

# pylint: disable=missing-function-docstring


def test_list_is_sequence():
    assert is_sequence([])


def test_tuple_is_sequence():
    assert is_sequence(())


def test_array_is_sequenc():
    assert is_sequence(np.array([]))


def test_set_is_sequence():
    assert is_sequence(set())


def test_dict_is_not_a_sequence():
    assert not is_sequence({})


def test_string_is_not_a_sequence():
    assert not is_sequence("abc")


def test_array_equal_with_nan():
    array1 = np.array([(1, 2.0, "a"), (3, np.nan, "b")], dtype=[("col1", "i4"), ("col2", "f4"), ("col3", "U1")])
    array2 = np.array([(1, 2.0, "a"), (3, np.nan, "b")], dtype=[("col1", "i4"), ("col2", "f4"), ("col3", "U1")])
    assert array_equal_with_nan(array1, array2)
