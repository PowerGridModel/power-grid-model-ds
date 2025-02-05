# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.enums.nodes import NodeType

# pylint: disable=missing-function-docstring


def test_grid_get_nearest_substation_node(basic_grid):
    substation_node = basic_grid.get_nearest_substation_node(node_id=103)
    assert NodeType.SUBSTATION_NODE == substation_node.node_type


def test_grid_get_nearest_substation_node_no_substation(basic_grid):
    substation_node = basic_grid.node.get(node_type=NodeType.SUBSTATION_NODE.value)
    basic_grid.delete_node(substation_node)

    with pytest.raises(RecordDoesNotExist):
        basic_grid.get_nearest_substation_node(node_id=103)


class TestGetDownstreamNodes:
    def test_get_downstream_nodes(self):
        grid = Grid.from_txt("S1 11", "S1 2", "2 3", "3 5", "5 6", "2 4", "4 99", "99 100")
        downstream_nodes = grid.get_downstream_nodes(node_id=3)
        assert [5, 6] == downstream_nodes

    def test_get_downstream_nodes_from_substation_node(self):
        grid = Grid.from_txt("S1 11", "S1 2", "2 3", "3 5", "5 6", "2 4", "4 99", "99 100")
        with pytest.raises(NotImplementedError):
            grid.get_downstream_nodes(node_id=1)


class TestGetBranchesInPath:
    def test_get_branches_in_path(self, basic_grid):
        branches = basic_grid.get_branches_in_path([106, 102, 101])
        np.testing.assert_array_equal(branches.id, [301, 201])

    def test_get_branches_in_path_inactive(self, basic_grid):
        branches = basic_grid.get_branches_in_path([101, 102, 103, 104, 105])
        # branch 203 is the normally open point should not be in the result
        np.testing.assert_array_equal(branches.id, [201, 202, 204, 601])

    def test_get_branches_in_path_one_node(self, basic_grid):
        branches = basic_grid.get_branches_in_path([106])
        assert 0 == branches.size

    def test_get_branches_in_path_empty_path(self, basic_grid):
        branches = basic_grid.get_branches_in_path([])
        assert 0 == branches.size


def test_component_three_winding_transformer(grid_with_3wt):
    component_list = grid_with_3wt.graphs.active_graph.get_components(
        grid_with_3wt.node.filter(node_type=NodeType.SUBSTATION_NODE.value).id
    )

    # check the components are as expected
    # use sets to make sure the order of the components is not important
    component_sets = set(frozenset(component) for component in component_list)
    assert component_sets == {frozenset({108, 109}), frozenset({107}), frozenset({105, 106}), frozenset({104})}

    path_1, distance_1 = grid_with_3wt.graphs.active_graph.get_shortest_path(101, 104)
    path_2, distance_2 = grid_with_3wt.graphs.active_graph.get_shortest_path(101, 107)
    assert path_1 == [101, 102, 104]
    assert path_2 == [101, 103, 107]
    assert distance_1 == 2
    assert distance_2 == 2
