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


def test_id_counter():
    container = FancyArrayContainer.empty()
    # pylint: disable=protected-access
    container._id_counter = 42
    assert 42 == container.id_counter


def test_branches(grid: Grid):
    node = NodeArray.zeros(10, empty_id=False)
    grid.append(node)
    grid.append(LineArray.zeros(10))
    grid.append(TransformerArray.zeros(10))
    grid.append(LinkArray.zeros(10))
    branches = grid.branches

    expected_ids = np.concatenate((grid.line.id, grid.transformer.id, grid.link.id))
    assert set(expected_ids) == set(branches.id)


def test_delete_node_without_additional_properties(basic_grid: Grid):
    assert 106 in basic_grid.node.id
    assert 106 in basic_grid.transformer["to_node"]

    original_grid = deepcopy(basic_grid)
    node = basic_grid.node.get(id=106)
    basic_grid.delete_node(node)

    assert 106 not in basic_grid.transformer["to_node"]
    assert 106 not in basic_grid.node.id
    assert len(original_grid.node) == len(basic_grid.node) + 1
    assert len(original_grid.transformer) == len(basic_grid.transformer) + 1


def test_delete_node_with_source(basic_grid: Grid):
    assert 101 in basic_grid.node.id
    assert 101 in basic_grid.source.node

    original_grid = deepcopy(basic_grid)
    node = basic_grid.node.get(id=101)
    basic_grid.delete_node(node)

    assert 101 not in basic_grid.node.id
    assert 101 not in basic_grid.source.node
    assert len(original_grid.node) == len(basic_grid.node) + 1
    assert len(original_grid.source) == len(basic_grid.source) + 1


def test_delete_node_with_load(basic_grid: Grid):
    assert 102 in basic_grid.node.id
    assert 102 in basic_grid.sym_load.node

    original_grid = deepcopy(basic_grid)
    node = basic_grid.node.get(id=102)
    basic_grid.delete_node(node)

    assert 102 not in basic_grid.node.id
    assert 102 not in basic_grid.sym_load.node
    assert len(original_grid.node) == len(basic_grid.node) + 1
    assert len(original_grid.sym_load) == len(basic_grid.sym_load) + 1


class TestGetTypedBranches:
    def test_get_typed_branches_transformer(self, basic_grid: Grid):
        grid = basic_grid

        transformer = grid.get_typed_branches([301])
        assert isinstance(transformer, TransformerArray)

    def test_get_typed_branches_line(self, basic_grid: Grid):
        grid = basic_grid

        line = grid.get_typed_branches([201])
        assert isinstance(line, LineArray)

    def test_get_typed_branches_link(self, basic_grid: Grid):
        grid = basic_grid

        link = grid.get_typed_branches([601])
        assert isinstance(link, LinkArray)

    def test_get_typed_branches_no_record(self, basic_grid: Grid):
        grid = basic_grid

        with pytest.raises(RecordDoesNotExist):
            grid.get_typed_branches([101])  # 101 is a node

    def test_get_typed_branches_no_input(self, basic_grid: Grid):
        grid = basic_grid

        with pytest.raises(ValueError):
            grid.get_typed_branches([])  # 101 is a node

    def test_get_typed_branches_array_input(self, basic_grid: Grid):
        lines = basic_grid.get_typed_branches(np.array([201, 202]))
        assert 2 == lines.size
        assert isinstance(lines, LineArray)

    def test_get_typed_branches_no_array_input(self, basic_grid: Grid):
        with pytest.raises(ValueError):
            basic_grid.get_typed_branches(np.array([]))


class TestReverseBranches:
    def test_reverse_line(self, basic_grid: Grid):
        line = basic_grid.line.get(from_node=102, to_node=103)
        basic_grid.reverse_branches(line)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=102, to_node=103)

        new_line = basic_grid.line.get(from_node=103, to_node=102)

        assert new_line.from_node == line.to_node
        assert new_line.to_node == line.from_node
        assert new_line.id == line.id

    def test_reverse_branch(self, basic_grid: Grid):
        branch = basic_grid.branches.get(from_node=101, to_node=102)
        basic_grid.reverse_branches(branch)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=101, to_node=102)

        new_branch = basic_grid.line.get(from_node=102, to_node=101)

        assert new_branch.from_node == branch.to_node
        assert new_branch.to_node == branch.from_node
        assert new_branch.id == branch.id

    def test_reverse_all_branches(self, basic_grid: Grid):
        from_nodes = basic_grid.branches.from_node
        to_nodes = basic_grid.branches.to_node

        basic_grid.reverse_branches(basic_grid.branches)

        assert np.all(from_nodes == basic_grid.branches.to_node)
        assert np.all(to_nodes == basic_grid.branches.from_node)

    def test_reverse_no_branches(self, basic_grid: Grid):
        basic_grid.reverse_branches(BranchArray())
