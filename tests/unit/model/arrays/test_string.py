# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from tests.fixtures.arrays import FancyTestArray, LongColumnNameFancyTestArray

# pylint: disable=missing-function-docstring


def test_str_small_array(fancy_test_array: FancyTestArray):
    array_str = str(fancy_test_array)

    rows = array_str.split("\n")
    assert len(rows) == 4


def test_str_empty_array():
    array = FancyTestArray()
    array_str = str(array)

    rows = array_str.split("\n")
    assert len(rows) == 2


def test_str_large_array():
    array = FancyTestArray.zeros(100)
    array.test_str = "ABC"
    array_str = str(array)

    splits = array_str.replace("\n", "|").split("|")
    separator = splits.pop(30)
    assert "(..90 hidden rows..)" in separator


def test_str_long_column_name():
    array = LongColumnNameFancyTestArray.zeros(2)
    array_str = array.as_table(column_width=15)

    splits = array_str.replace("\n", "|").split("|")
    split_lengths = (len(split) for split in splits)
    assert all((length == 15 for length in split_lengths))
    assert "this_is_a_ver.." in array_str


def test_str_long_values():
    array = FancyTestArray.zeros(1)
    array.test_str = "this_is_a_very_long_value"
    array.test_int = 112233445566778899
    array_str = array.as_table(column_width=15)

    splits = array_str.replace("\n", "|").split("|")
    split_lengths = (len(split) for split in splits)
    assert all((length == 15 for length in split_lengths))
    assert "|1122334455667..|" in array_str
    assert "|this_is_a_ver.." in array_str


def test_str_long_column_name_autosize():
    array = LongColumnNameFancyTestArray.zeros(2)
    array_str = str(array)
    assert "this_is_a_very_long_column_name |" in array_str


def test_str_long_values_autosize():
    array = FancyTestArray.zeros(1)
    array.test_str = "this_is_a_very_long_value"
    array.test_int = 112233445566778899
    array_str = str(array)
    assert "| this_is_a_very_long_value" in array_str
    assert "| 112233445566778899" in array_str


def test_str_in_loop(fancy_test_array: FancyTestArray):
    for row in fancy_test_array:
        assert str(row)
