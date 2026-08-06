# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Various tests for the FancyArrayContainer."""

import re
from copy import deepcopy
from dataclasses import dataclass

import pytest

from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.containers.base import FancyArrayContainer
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds.arrays import (
    IdArray,
    LineArray,
    LinkArray,
    NodeArray,
    TransformerArray,
)
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
    assert len(list(container.all_arrays())) == 2
    array_1_id = id(container.array_1)
    all_arrays = list(container.all_arrays())
    assert array_1_id == id(all_arrays[0])


def test_check_ids_no_arrays():
    container = FancyArrayContainer.empty()
    assert len(list(container.all_arrays())) == 0
    container.check_ids()


def test_check_ids_two_empty_arrays():
    container = _TwoArraysContainer.empty()
    assert len(list(container.all_arrays())) == 2
    container.check_ids()


def test_check_ids_4_arrays_3_with_id():
    container = _FourArraysContainer.empty()
    assert len(list(container.all_arrays())) == 4
    container.check_ids()


def test_check_ids_two_arrays_no_conflicts():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(1)
    container.array_1.id = 1
    container.array_2 = IdArray.zeros(1)
    container.array_1.id = 2

    assert len(list(container.all_arrays())) == 2
    container.check_ids()


def test_check_ids_two_arrays_with_conflict():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(1)
    container.array_1.id = 1
    container.array_2 = IdArray.zeros(1)
    container.array_2.id = 1

    assert len(list(container.all_arrays())) == 2

    with pytest.raises(ValueError, match="Duplicates found within _TwoArraysContainer!"):
        container.check_ids()


def test_check_ids_two_arrays_with_conflict_in_same_array():
    container = _TwoArraysContainer.empty()
    container.array_1 = IdArray.zeros(2)
    container.array_1.id = [1, 1]
    container.array_2 = IdArray.zeros(1)
    container.array_2.id = 2

    assert len(list(container.all_arrays())) == 2

    with pytest.raises(ValueError, match="Duplicates found within _TwoArraysContainer!"):
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
    with pytest.raises(ValueError, match=re.escape("Cannot append, array contains ids that already exist: {3}")):
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


def test_rebuild_ids():
    grid = Grid.from_txt("1 2 20", "2 3 21", "10 11 22")
    expected_ids = {1, 2, 3, 10, 11, 20, 21, 22}
    assert grid.ids == expected_ids
    grid._ids = set()
    grid._max_id = 0
    grid.rebuild_ids()
    assert grid.ids == expected_ids
    assert grid.max_id == max(expected_ids)


def test_rebuild_ids_with_duplicates():
    grid = Grid.from_txt("1 2 12")
    grid.node.id = [1, 12]  # Duplicate IDs within different arrays same array
    with pytest.raises(ValueError, match=re.escape("Duplicate ids found between arrays (LineArray)")):
        grid.rebuild_ids()


def test_ids():
    grid = Grid.from_txt("1 2 20", "2 3 21", "10 11 22")
    assert grid.ids == {1, 2, 3, 10, 11, 20, 21, 22}


def test_max_id_empty_container():
    container = FancyArrayContainer.empty()
    assert container.max_id == 0
    assert container._max_id == 0


def test_max_id_after_append_with_explicit_ids():
    grid = Grid.empty()
    nodes = NodeArray.zeros(3)
    nodes.id = [1, 2, 5]
    grid.append(nodes)
    assert grid.max_id == 5
    assert grid._max_id == 5


def test_max_id_after_append_with_lower_ids():
    grid = Grid.empty()
    nodes = NodeArray.zeros(2)
    nodes.id = [10, 20]
    grid.append(nodes)
    assert grid.max_id == 20

    lines = LineArray.zeros(2)
    lines.id = [3, 4]
    lines.from_node = [10, 10]
    lines.to_node = [20, 20]
    grid.append(lines)
    assert grid.max_id == 20
    assert grid._max_id == 20


def test_max_id_after_append_with_higher_ids():
    grid = Grid.empty()
    nodes = NodeArray.zeros(2)
    nodes.id = [1, 2]
    grid.append(nodes)
    assert grid.max_id == 2

    more_nodes = NodeArray.zeros(2)
    more_nodes.id = [8, 9]
    grid.append(more_nodes)
    assert grid.max_id == 9
    assert grid._max_id == 9


def test_max_id_after_attach_ids():
    grid = Grid.empty()
    nodes = NodeArray.zeros(3)
    grid.append(nodes)  # empty ids -> attach_ids
    assert set(grid.node.id.tolist()) == {1, 2, 3}
    assert grid.max_id == 3
    assert grid._max_id == 3

    more_nodes = NodeArray.zeros(2)
    grid.append(more_nodes)
    assert set(more_nodes.id.tolist()) == {4, 5}
    assert grid.max_id == 5
    assert grid._max_id == 5


def test_max_id_attach_ids_directly():
    grid = Grid.empty()
    nodes = NodeArray.zeros(2)
    grid.attach_ids(nodes)
    assert nodes.id.tolist() == [1, 2]
    assert grid.max_id == 2
    assert grid.ids == {1, 2}


def test_max_id_after_rebuild_ids_decreases():
    grid = Grid.from_txt("1 2 20", "2 3 21", "10 11 22")
    assert grid.max_id == 22

    grid.node = grid.node.exclude(id=11)
    grid.line = grid.line.exclude(id=22)
    grid.rebuild_ids()

    assert grid.ids == {1, 2, 3, 10, 20, 21}
    assert grid.max_id == 21
    assert grid._max_id == 21


def test_max_id_after_rebuild_ids_empty():
    grid = Grid.empty()
    grid._ids = {99}
    grid._max_id = 99
    grid.rebuild_ids()
    assert grid.ids == set()
    assert grid.max_id == 0


def test_max_id_after_delete_via_grid_api():
    grid = Grid.from_txt("1 2 20", "2 3 21", "10 11 22")
    assert grid.max_id == 22

    branch = grid.line.get(id=22)
    grid.delete_branch(branch)
    assert 22 not in grid.ids
    assert grid.max_id == 21


def test_max_id_deepcopy():
    grid = Grid.from_txt("1 2 20", "2 3 21")
    copied = deepcopy(grid)
    assert copied.max_id == grid.max_id
    assert copied._max_id == grid._max_id
