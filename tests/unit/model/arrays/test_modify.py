# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from power_grid_model_ds._core import fancypy as fp
from tests.fixtures.arrays import FancyNonIdArray, FancyTestArray

# pylint: disable=missing-function-docstring,missing-class-docstring


class TestReorder:
    def test_reorder_by_id(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        reordered = fancy_test_array.re_order([3, 1, 2])
        assert_array_equal(reordered.id, [3, 1, 2])
        assert_array_equal(reordered.test_str, ["d", "a", "c"])

    def test_reorder_by_test_str(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        reordered = fancy_test_array.re_order(["d", "a", "c"], column="test_str")
        assert_array_equal(reordered.id, [3, 1, 2])
        assert_array_equal(reordered.test_str, ["d", "a", "c"])

    def test_reorder_mismatched_length(self, fancy_test_array: FancyTestArray):
        with pytest.raises(ValueError):
            fancy_test_array.re_order([3, 1])


class TestUpdateById:
    def test_get_update_by_id(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        updated = fancy_test_array.get_updated_by_id([1, 3], test_str="e")

        assert_array_equal(updated.id, [1, 3])
        assert_array_equal(updated.test_str, ["e", "e"])

        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["e", "c", "e"])

    def test_get_update_by_id_duplicate_id_input(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        updated = fancy_test_array.get_updated_by_id([1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3], test_str="e")

        assert_array_equal(updated.id, [1, 3])

    def test_update_by_id_multiple_columns(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        fancy_test_array.update_by_id([1, 3], test_str="e", test_int=[88, 99])
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["e", "c", "e"])
        assert_array_equal(fancy_test_array.test_int, [88, 0, 99])

    def test_update_by_id_invalid_column(self, fancy_test_array: FancyTestArray):
        with pytest.raises(ValueError):
            fancy_test_array.update_by_id([1, 3], non_existing_column=123)

    def test_update_by_id_invalid_length(self, fancy_test_array: FancyTestArray):
        with pytest.raises(ValueError):
            fancy_test_array.update_by_id([1, 3], test_str=["e", "f", "g"])

    def test_update_by_id_invalid_id(self, fancy_test_array: FancyTestArray):
        with pytest.raises(ValueError):
            fancy_test_array.update_by_id([1, 4], test_str="e")

    def test_update_by_id_invalid_id_allow_missing(self, fancy_test_array: FancyTestArray):
        fancy_test_array.update_by_id([1, 4], test_str="e", allow_missing=True)
        assert fancy_test_array.get(1).record.test_str == "e"

    def test_update_by_id_no_id_column(self):
        fancy_non_id_array = FancyNonIdArray.zeros(10)
        with pytest.raises(ValueError):
            fancy_non_id_array.update_by_id([1, 4], test_str="e")

    def test_update_by_id_non_existing_id(self, fancy_test_array: FancyTestArray):
        with pytest.raises(ValueError):
            fancy_test_array.update_by_id([1, 4], test_str="e")


class TestConcatenate:
    def test_concatenate_fancy_array(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        concatenated = fp.concatenate(fancy_test_array, fancy_test_array)
        assert_array_equal(concatenated.id, [1, 2, 3, 1, 2, 3])
        assert_array_equal(concatenated.test_str, ["a", "c", "d", "a", "c", "d"])

    def test_concatenate_to_empty_array(self, fancy_test_array: FancyTestArray):
        empty_array = FancyTestArray()
        concatenated = fp.concatenate(empty_array, fancy_test_array)
        assert fp.array_equal(fancy_test_array, concatenated)

    def test_concatenate_empty_arrays(self):
        empty_array = FancyTestArray()
        concatenated = fp.concatenate(empty_array, FancyTestArray())
        assert concatenated.size == 0

    def test_concatenate_multiple_fancy_arrays(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        concatenated = fp.concatenate(fancy_test_array, fancy_test_array, fancy_test_array)
        assert_array_equal(concatenated.id, [1, 2, 3, 1, 2, 3, 1, 2, 3])
        assert_array_equal(concatenated.test_str, ["a", "c", "d", "a", "c", "d", "a", "c", "d"])

    def test_concatenate_ndarray(self, fancy_test_array: FancyTestArray):
        assert_array_equal(fancy_test_array.id, [1, 2, 3])
        assert_array_equal(fancy_test_array.test_str, ["a", "c", "d"])
        concatenated = fp.concatenate(fancy_test_array, fancy_test_array.data)
        assert_array_equal(concatenated.id, [1, 2, 3, 1, 2, 3])
        assert_array_equal(concatenated.test_str, ["a", "c", "d", "a", "c", "d"])

    def test_concatenate_different_fancy_array(self, fancy_test_array: FancyTestArray):
        different_array = FancyNonIdArray.zeros(10)
        with pytest.raises(TypeError):
            fp.concatenate(fancy_test_array, different_array)

    def test_concatenate_different_ndarray(self, fancy_test_array: FancyTestArray):
        different_array = FancyNonIdArray.zeros(10)
        with pytest.raises(TypeError):
            fp.concatenate(fancy_test_array, different_array.data)

    def test_concatenate_different_fancy_array_same_dtype(self, fancy_test_array: FancyTestArray):
        sub_array = fancy_test_array[["test_str", "test_int"]]

        different_array = FancyNonIdArray.zeros(10)
        different_sub_array = different_array[["test_str", "test_int"]]

        concatenated = np.concatenate([sub_array, different_sub_array])
        assert concatenated.size == 13
