# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from typing import ClassVar

import numpy as np
import pytest

from power_grid_model_ds._core.utils.misc import (
    array_equal_with_nan,
    combine_attribute_from_parent_classes,
    get_public_annotations,
    is_sequence,
)

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


class _ParentClass:
    a: ClassVar[set[int]] = {1, 2, 3}
    b: ClassVar[dict[int, str]] = {1: "a", 2: "b", 3: "c"}
    c: ClassVar[list[int]] = [1, 2, 3]


class _ChildClass(_ParentClass):
    a: ClassVar[set[int]] = {3, 4, 5}
    b: ClassVar[dict[int, str]] = {2: "b", 3: "ccc"}
    c: ClassVar[list[int]] = [3, 4, 5]


def test_get_public_class_attrs():
    assert get_public_annotations(_ParentClass) == {
        "a": ClassVar[set[int]],
        "b": ClassVar[dict[int, str]],
        "c": ClassVar[list[int]],
    }


def test_combine_attribute_from_parent_classes_set():
    attr = combine_attribute_from_parent_classes(_ChildClass, attribute_name="a", attribute_type=set)
    assert attr == {1, 2, 3, 4, 5}


def test_combine_attribute_from_parent_classes_dict():
    assert _ChildClass.b == {2: "b", 3: "ccc"}
    attr = combine_attribute_from_parent_classes(_ChildClass, attribute_name="b", attribute_type=dict)
    assert attr == {1: "a", 2: "b", 3: "ccc"}


def test_combine_attribute_from_parent_classes_list():
    with pytest.raises(NotImplementedError):
        combine_attribute_from_parent_classes(_ChildClass, attribute_name="c", attribute_type=list)
