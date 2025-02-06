# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Grid tests"""

from collections import Counter

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from power_grid_model_ds.errors import MissingBranchError, MissingNodeError, NoPathBetweenNodes

# pylint: disable=missing-function-docstring,missing-class-docstring


class TestBasicGraphFunctions:
    def test_graph_add_node_and_branch(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)

        # both nodes exist in the external2graph mapping
        assert 1 in graph.external_ids
        assert 2 in graph.external_ids
        # the graph has the correct size
        assert 2 == graph.nr_nodes
        assert 1 == graph.nr_branches

    def test_add_invalid_branch(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)
        assert graph.has_branch(1, 2)

        with pytest.raises(MissingNodeError):
            graph.add_branch(1, 3)

    def test_has_node(self, graph):
        graph.add_node(1)
        assert graph.has_node(1)
        assert not graph.has_node(2)

    def test_has_branch(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)

        assert graph.has_branch(1, 2)
        assert graph.has_branch(2, 1)  # reversed should work too
        assert not graph.has_branch(1, 3)

    def test_graph_all_branches(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)

        assert [(1, 2)] == list(graph.all_branches)

    def test_graph_all_branches_parallel(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)
        graph.add_branch(1, 2)
        graph.add_branch(2, 1)

        assert [(1, 2), (1, 2), (2, 1)] == list(graph.all_branches)

    def test_delete_invalid_node_without_error(self, graph):
        graph.delete_node(3, raise_on_fail=False)

    def test_delete_invalid_branch_without_error(self, graph):
        graph.delete_branch(1, 3, raise_on_fail=False)

    def test_graph_delete_connected_node(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)

        graph.delete_node(1)  # also deletes branch 1-2

        assert 1 == graph.nr_nodes
        assert 0 == graph.nr_branches
        assert 2 in graph.external_ids
        assert 1 not in graph.external_ids
        assert not graph.has_branch(1, 2)

    def test_remove_invalid_node(self, graph):
        graph.add_node(1)
        graph.add_node(2)

        with pytest.raises(MissingNodeError):
            graph.delete_node(3)

    def test_remove_invalid_branch(self, graph):
        graph.add_node(1)
        graph.add_node(2)

        with pytest.raises(MissingBranchError):
            graph.delete_branch(1, 3)

        with pytest.raises(MissingBranchError):
            graph.delete_branch(1, 2)

    # pylint: disable=protected-access
    def test_internal_ids_after_node_deletion(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_node(3)

        internal_id_0 = graph.external_to_internal(1)
        internal_id_1 = graph.external_to_internal(2)
        internal_id_2 = graph.external_to_internal(3)
        assert graph._has_node(internal_id_0)
        assert graph._has_node(internal_id_1)
        assert graph._has_node(internal_id_2)

        # now delete node 2, this can change the internal mapping
        graph.delete_node(2)

        internal_id_0 = graph.external_to_internal(1)
        internal_id_2 = graph.external_to_internal(3)

        assert graph._has_node(internal_id_0)
        assert graph._has_node(internal_id_2)

    def test_graph_in_branches(self, graph):
        graph.add_node(1)
        graph.add_node(2)
        graph.add_branch(1, 2)
        graph.add_branch(1, 2)
        graph.add_branch(2, 1)

        assert [(2, 1), (2, 1), (2, 1)] == list(graph.in_branches(1))
        assert [(1, 2), (1, 2), (1, 2)] == list(graph.in_branches(2))


def test_tmp_remove_nodes(graph_with_2_routes) -> None:
    graph = graph_with_2_routes

    assert graph.nr_branches == 4

    # add parallel branches to test whether they are restored correctly
    graph.add_branch(1, 5)
    graph.add_branch(5, 1)

    assert graph.nr_nodes == 5
    assert graph.nr_branches == 6

    before_sets = [frozenset(branch) for branch in graph.all_branches]
    counter_before = Counter(before_sets)

    with graph.tmp_remove_nodes([1, 2]):
        assert graph.nr_nodes == 3
        assert list(graph.all_branches) == [(5, 4)]

    assert graph.nr_nodes == 5
    assert graph.nr_branches == 6

    after_sets = [frozenset(branch) for branch in graph.all_branches]
    counter_after = Counter(after_sets)
    assert counter_before == counter_after


def test_get_components(graph_with_2_routes):
    graph = graph_with_2_routes
    graph.add_node(99)
    graph.add_branch(1, 99)
    substation_nodes = np.array([1])

    components = graph.get_components(substation_nodes=substation_nodes)

    assert len(components) == 3
    assert set(components[0]) == {2, 3}
    assert set(components[1]) == {4, 5}
    assert set(components[2]) == {99}


def test_from_arrays(basic_grid):
    new_graph = basic_grid.graphs.complete_graph.__class__.from_arrays(basic_grid)
    assert_array_equal(new_graph.external_ids, basic_grid.node.id)


class TestPathMethods:
    def test_get_shortest_path(self, graph_with_2_routes):
        graph = graph_with_2_routes
        path = graph.get_shortest_path(1, 3)
        assert path == ([1, 2, 3], 2)

    def test_shortest_path_on_circular_network(self, graph_with_5_nodes):
        graph_with_5_nodes.add_branch(1, 2)
        graph_with_5_nodes.add_branch(2, 3)

        path, length = graph_with_5_nodes.get_shortest_path(1, 3)

        assert path == [1, 2, 3]
        assert length == 2

        path, length = graph_with_5_nodes.get_shortest_path(1, 1)
        assert path == [1]
        assert length == 0

    def test_shortest_path_no_path(self, graph_with_5_nodes):
        graph_with_5_nodes.add_branch(1, 2)
        graph_with_5_nodes.add_branch(3, 4)
        graph_with_5_nodes.add_branch(4, 5)

        with pytest.raises(NoPathBetweenNodes):
            graph_with_5_nodes.get_shortest_path(1, 5)

    def test_all_paths_on_circular_network(self, graph_with_5_nodes):
        graph_with_5_nodes.add_branch(1, 2)
        graph_with_5_nodes.add_branch(2, 3)
        graph_with_5_nodes.add_branch(3, 4)
        graph_with_5_nodes.add_branch(4, 5)
        graph_with_5_nodes.add_branch(5, 1)

        paths = graph_with_5_nodes.get_all_paths(1, 3)

        assert len(paths) == 2
        assert [1, 2, 3] in paths
        assert [1, 5, 4, 3] in paths

    def test_all_paths_no_path(self, graph_with_5_nodes):
        with pytest.raises(NoPathBetweenNodes):
            graph_with_5_nodes.get_all_paths(1, 2)


class TestFindFundamentalCycles:
    @pytest.mark.parametrize(
        "additional_edges, nodes_in_cycles",
        [
            ([], set()),
            ([(2, 5)], {1, 2, 5}),
            ([(1, 2)], {1, 2}),
            ([(1, 2), (1, 2)], {1, 2}),
            ([(2, 4)], {1, 2, 4, 5}),
            ([(1, 5), (3, 5)], {1, 2, 3, 5}),
        ],
    )
    def test_find_fundamental_cycles(self, graph_with_2_routes, additional_edges, nodes_in_cycles):
        graph = graph_with_2_routes
        for u, v in additional_edges:
            graph.add_branch(u, v)

        result = graph.find_fundamental_cycles()
        assert len(result) == len(set(additional_edges))
        for node_path in result:
            assert node_path[0] == node_path[-1]
            assert len(node_path) == len(set(node_path)) + 1
            assert all(node in nodes_in_cycles for node in node_path)

    def test_find_fundamental_cycles_multiple_trees(self, graph):
        """The following graph contains 2 unconnected subgraphs of 4 nodes each.
        Both subgraphs contain a cycle.
        Visual representation:
            Subgraph 1:
                1 -- 2
                |    |
                4 -- 3
            Subgraph 2:
            5 - 6 -- 7
                |    |
                '--- 8
        """
        edges = [(1, 2), (2, 3), (3, 4), (1, 4), (5, 6), (6, 7), (6, 8), (7, 8)]
        for _id in range(1, 9):
            graph.add_node(_id)
        for u, v in edges:
            graph.add_branch(u, v)

        # The MST is not unique, so the node paths can be in any order.
        # For example: [1,2,3,4,1] and [4,3,2,1,4] are both valid return values.
        # We do know exactly which nodes are in the cycle and that the first and last node are the same.
        result = graph.find_fundamental_cycles()
        result_as_sets = {frozenset(nodes) for nodes in result}
        assert len(result) == 2
        assert frozenset([1, 2, 3, 4]) in result_as_sets
        assert frozenset([6, 7, 8]) in result_as_sets
        assert result[0][0] == result[0][-1]
        assert result[1][0] == result[1][-1]


class TestGetConnected:
    def test_get_connected_exclusive(self, graph_with_2_routes):
        graph = graph_with_2_routes
        connected_nodes = graph.get_connected(node_id=1)

        assert {2, 5, 3, 4} == set(connected_nodes)
        assert set(connected_nodes[:2]) == {2, 5}
        assert set(connected_nodes[2:]) == {3, 4}

    def test_get_connected_inclusive(self, graph_with_2_routes):
        graph = graph_with_2_routes

        connected_nodes = graph.get_connected(node_id=1, inclusive=True)

        assert {1, 2, 3, 4, 5} == set(connected_nodes)

    def test_get_connected_with_unconnected_route(self, graph_with_2_routes):
        graph = graph_with_2_routes
        graph.add_node(9)
        graph.add_node(10)
        graph.add_node(11)
        graph.add_branch(9, 10)  # Route 3 - unconnected
        graph.add_branch(10, 11)  # Route 3 - unconnected

        connected_nodes = graph.get_connected(node_id=1, inclusive=True)
        assert {1, 2, 3, 4, 5} == set(connected_nodes)

        connected_nodes = graph.get_connected(node_id=9, inclusive=True)
        assert {9, 10, 11} == set(connected_nodes)

    def test_get_connected_ignore_single_node(self, graph_with_2_routes):
        graph = graph_with_2_routes
        connected_nodes = graph.get_connected(node_id=1, nodes_to_ignore=[4])

        assert {2, 3, 5} == set(connected_nodes)

    def test_get_connected_ignore_multiple_nodes(self, graph_with_2_routes):
        graph = graph_with_2_routes
        connected_nodes = graph.get_connected(node_id=1, nodes_to_ignore=[2, 4])

        assert {5} == set(connected_nodes)


class TestFindFirstConnected:
    def test_find_first_connected(self, graph_with_2_routes):
        graph = graph_with_2_routes
        assert 2 == graph.find_first_connected(1, candidate_node_ids=[2, 3, 4])

    def test_find_first_connected_same_node(self, graph_with_2_routes):
        graph = graph_with_2_routes
        with pytest.raises(ValueError):
            graph.find_first_connected(1, candidate_node_ids=[1, 3, 5])

    def test_find_first_connected_no_match(self, graph_with_2_routes):
        graph = graph_with_2_routes
        graph.add_node(99)
        with pytest.raises(MissingNodeError):
            graph.find_first_connected(1, candidate_node_ids=[99])
