# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Various tests for the FancyArrayContainer."""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np
import pytest

from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    BranchArray,
    IdArray,
    LineArray,
    LinkArray,
    NodeArray,
    TransformerArray,
)
from power_grid_model_ds._core.model.containers.base import FancyArrayContainer
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import FancyNonIdArray

# pylint: disable=missing-function-docstring,missing-class-docstring


@dataclass
class _TwoArraysContainer(FancyArrayContainer):
    array_1: IdArray
    array_2: IdArray


@dataclass
class _FourArraysContainer(_TwoArraysContainer):
    array_3_no_id: IdArray
    array_4_no_id: FancyNonIdArray


def test_id_counter_type(self, basic_grid: Grid):
    assert isinstance(basic_grid.id_counter, int)


def test_id_counter():
    container = FancyArrayContainer.empty()
    # pylint: disable=protected-access
    container._id_counter = 42
    assert 42 == container.id_counter



def test_deepcopy():
    container = Grid.empty()
    container.node = NodeArray.zeros(1)
    container.line = LineArray.zeros(1)
    container.transformer = TransformerArray.zeros(1)
    container.link = LinkArray.zeros(1)

    copied_container = deepcopy(container)

    assert container.node.id == copied_container.node.id
    assert container.line.id == copied_container.line.id
    assert container.transformer.id == copied_container.transformer.id
    assert container.link.id == copied_container.link.id


def test_all_arrays():
    container = _TwoArraysContainer.empty()
    assert 2 == len(list(container.all_arrays()))
    array_1_id = id(container.array_1)
    all_arrays = list(container.all_arrays())
    assert array_1_id == id(all_arrays[0])


def test_check_ids_no_arrays():
    container = FancyArrayContainer.empty()
    assert 0 == len(list(container.all_arrays()))
    container.check_ids()


def test_check_ids_two_empty_arrays():
    container = _TwoArraysContainer.empty()
    assert 2 == len(list(container.all_arrays()))
    container.check_ids()


def test_check_ids_4_arrays_3_with_id():
    container = _FourArraysContainer.empty()
    assert 4 == len(list(container.all_arrays()))
    container.check_ids()


def test_check_ids_two_arrays_no_conflicts():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(1)
    container.array_1.id = 1
    container.array_2 = IdArray.zeros(1)
    container.array_1.id = 2

    assert 2 == len(list(container.all_arrays()))
    container.check_ids()


def test_check_ids_two_arrays_with_conflict():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(1)
    container.array_1.id = 1
    container.array_2 = IdArray.zeros(1)
    container.array_2.id = 1

    assert 2 == len(list(container.all_arrays()))

    with pytest.raises(ValueError):
        container.check_ids()


def test_check_ids_two_arrays_with_conflict_in_same_array():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(2)
    container.array_1.id = [1, 1]
    container.array_2 = IdArray.zeros(1)
    container.array_2.id = 2

    assert 2 == len(list(container.all_arrays()))

    with pytest.raises(ValueError):
        container.check_ids()


def test_search_for_id_no_arrays():
    container = FancyArrayContainer.empty()
    with pytest.raises(RecordDoesNotExist):
        container.search_for_id(99)


def test_search_for_id_match_in_two_arrays():
    container = Grid.empty()
    container.node = NodeArray.zeros(1)
    container.node.id = 42

    container.line = LineArray.zeros(1)
    container.line.id = 42
    result = container.search_for_id(42)

    expected_result = [container.node[0:1], container.line[0:1]]

    assert expected_result == result


def test_search_for_id_no_match_in_two_arrays():
    container = Grid.empty()
    container.node = NodeArray.zeros(1)
    container.node.id = 41

    container.line = LineArray.zeros(1)
    container.line.id = 42

    with pytest.raises(RecordDoesNotExist):
        container.search_for_id(43)


def test_append_with_overlapping_ids():
    """Test that appending arrays with overlapping IDs raises an error."""
    grid = Grid.empty()

    # Create first array with IDs [1, 2, 3]
    nodes_1 = NodeArray.zeros(3)
    nodes_1.id = [1, 2, 3]
    grid.append(nodes_1)

    # Create second array with overlapping IDs [3, 4, 5] (ID 3 overlaps)
    nodes_2 = NodeArray.zeros(3)
    nodes_2.id = [3, 4, 5]

    # This should raise a ValueError due to overlapping ID 3
    with pytest.raises(ValueError, match="Cannot append: minimum id 3 is not greater than the current id counter 3"):
        grid.append(nodes_2)


def test_append_with_non_overlapping_ids():
    """Test that appending arrays with non-overlapping IDs works correctly."""
    grid = Grid.empty()

    # Create first array with IDs [1, 2, 3]
    nodes_1 = NodeArray.zeros(3)
    nodes_1.id = [1, 2, 3]
    grid.append(nodes_1)

    # Create second array with non-overlapping IDs [4, 5, 6]
    nodes_2 = NodeArray.zeros(3)
    nodes_2.id = [4, 5, 6]

    # This should work without error
    grid.append(nodes_2)

    # Verify all nodes are in the grid
    assert grid.node.size == 6
    expected_ids = [1, 2, 3, 4, 5, 6]
    assert sorted(grid.node.id.tolist()) == expected_ids
