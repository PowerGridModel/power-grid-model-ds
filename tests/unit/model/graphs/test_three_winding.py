# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel
from power_grid_model_ds.arrays import NodeArray, ThreeWindingTransformerArray


@pytest.fixture
def branch3_array() -> ThreeWindingTransformerArray:
    three = ThreeWindingTransformerArray.empty(2)
    three.node_1 = [2, 20]
    three.node_2 = [3, 30]
    three.node_3 = [5, 50]
    three.status_1 = [1, 1]
    three.status_2 = [1, 1]
    three.status_3 = [0, 0]

    return three


def _setup_graph(graph: RustworkxGraphModel, branch3_array: ThreeWindingTransformerArray) -> None:
    nodes = NodeArray.empty(12)
    nodes.id = [1, 2, 3, 4, 5, 6, 10, 20, 30, 40, 50, 60]

    graph.add_node_array(nodes)

    # The three winding arrays are open at 5 and 50.
    #                            -------------------
    #                            |                 |
    # 1 -- 2 --- 3 -- 4         10 -- 20 --- 30 -- 40
    #         |                  |        |        |
    #         5                  |        50       |
    #         |                  |        |        |
    #         6                  ---------60--------
    graph.add_branch3_array(branch3_array)

    graph.add_branch(1, 2)
    graph.add_branch(3, 4)
    graph.add_branch(5, 6)

    graph.add_branch(10, 20)
    graph.add_branch(30, 40)
    graph.add_branch(50, 60)

    graph.add_branch(10, 60)
    graph.add_branch(10, 40)
    graph.add_branch(40, 60)
    return graph


@pytest.fixture(params=[True, False], ids=["active", "complete"])
def active_only(request):
    return request.param


@pytest.fixture
def graph(active_only, branch3_array):
    return _setup_graph(RustworkxGraphModel(active_only=active_only), branch3_array)


def list_of_paths_to_set(paths, ordered_paths=False):
    if ordered_paths:
        return {tuple(path) for path in paths}
    return {tuple(sorted(path)) for path in paths}


@pytest.mark.usefixtures("graph")
class TestThreeWindingRegistration:
    def test_three_winding_transformer_group(self, graph):
        assert graph._three_winding_nodes == {(2, 3, 5), (20, 30, 50)}

    def test_three_winding_transformer_group_removed(self, graph, branch3_array):
        graph.delete_branch3_array(branch3_array.filter(node_1=2))
        assert graph._three_winding_nodes == {(20, 30, 50)}

        assert graph.delete_branch3_array(branch3_array.filter(node_1=20)) is None
        assert graph._three_winding_nodes == set()


@pytest.mark.usefixtures("graph")
class TestThreeWindingHelpers:
    def test_branches_to_remove(self, graph, active_only):
        expected = [] if active_only else [(3, 5), (30, 50)]
        assert sorted(graph._branches_to_remove_from_three_winding_transformers()) == expected

    def test_squash_of_paths(self, graph):
        paths = [[1, 2, 3, 5, 6], [10, 20, 50, 60]]
        expected_paths = [[1, 2, 5, 6], [10, 20, 50, 60]]
        assert graph._squash_paths_inside_three_winding_transformers(paths) == expected_paths


@pytest.mark.usefixtures("graph")
class TestGetAllPaths:
    @pytest.mark.parametrize(
        ("source", "dest", "active_expected", "complete_expected"),
        [
            pytest.param(1, 6, set(), {(1, 2, 5, 6)}, id="1->6"),
            pytest.param(1, 5, set(), {(1, 2, 5)}, id="1->5"),
            pytest.param(
                10,
                50,
                {
                    (10, 40, 60, 50),
                    (10, 60, 50),
                    (10, 20, 30, 40, 60, 50),
                },
                {
                    (10, 40, 60, 50),
                    (10, 40, 30, 50),
                    (10, 60, 40, 30, 50),
                    (10, 60, 50),
                    (10, 20, 50),
                    (10, 20, 30, 40, 60, 50),
                },
                id="10->50",
            ),
        ],
    )
    def test_get_all_paths(self, graph, active_only, source, dest, active_expected, complete_expected):
        expected = active_expected if active_only else complete_expected
        actual_paths = graph.get_all_paths(source, dest)

        assert list_of_paths_to_set(actual_paths, ordered_paths=True) == expected

    @pytest.mark.parametrize(
        ("source", "dest", "active_expected", "complete_expected"),
        [
            pytest.param(1, 6, set(), {(1, 2, 5, 6)}, id="1->6"),
            pytest.param(1, 5, set(), {(1, 2, 5)}, id="1->5"),
            pytest.param(
                10,
                50,
                {
                    (10, 40, 60, 50),
                    (10, 60, 50),
                },
                {
                    (10, 60, 50),
                    (10, 40, 60, 50),
                    (10, 40, 30, 50),
                    (10, 60, 40, 30, 50),
                    (10, 20, 50),
                },
                id="10->50",
            ),
        ],
    )
    def test_get_all_paths_removed_branch(self, graph, active_only, source, dest, active_expected, complete_expected):
        expected = active_expected if active_only else complete_expected
        with graph.tmp_remove_branches([(2, 3), (20, 30)]):
            actual_paths = graph.get_all_paths(source, dest)

        assert list_of_paths_to_set(actual_paths, ordered_paths=True) == expected


class TestGetCycles:
    def test_get_cycles(self, graph):
        expected = (
            {(10, 20, 30, 40, 10), (40, 30, 20, 10, 60, 40)}
            if graph.active_only
            else {(10, 20, 30, 40, 10), (40, 30, 50, 60, 40), (10, 20, 50, 60, 10)}
        )
        actual_cycles = graph.find_fundamental_cycles()
        assert {tuple(cycle) for cycle in actual_cycles} == expected

    def test_get_cycles_removed_branch(self, graph):
        branches_to_remove = [(2, 3), (20, 30)] if graph.active_only else [(2, 3), (3, 5), (20, 30), (30, 50)]
        expected = {(40, 10, 60, 40)} if graph.active_only else {(40, 10, 20, 50, 60, 40), (10, 20, 50, 60, 10)}

        with graph.tmp_remove_branches(branches_to_remove):
            actual_cycles = graph.find_fundamental_cycles()
        assert {tuple(cycle) for cycle in actual_cycles} == expected


class TestGraphRemainingFunctions:
    def test_nr_branches(self, graph, active_only):
        expected = 11 if active_only else 15
        assert graph.nr_branches == expected

    def test_get_components(self, graph, active_only):
        expected = (
            {(1, 2, 3, 4), (5, 6), (10, 20, 30, 40, 50, 60)}
            if active_only
            else {(1, 2, 3, 4, 5, 6), (10, 20, 30, 40, 50, 60)}
        )
        actual_components = graph.get_components()
        assert list_of_paths_to_set(actual_components) == expected

        with graph.tmp_remove_nodes([2, 60]):
            expected = (
                {(1,), (3, 4), (5, 6), (10, 20, 30, 40), (50,)}
                if active_only
                else {(1,), (3, 4, 5, 6), (10, 20, 30, 40, 50)}
            )
            assert list_of_paths_to_set(graph.get_components()) == list_of_paths_to_set(expected)

    def test_all_branches(self, graph, active_only):
        expected_edges = {
            (1, 2),
            (2, 3),
            (3, 4),
            (5, 6),
            (10, 20),
            (20, 30),
            (30, 40),
            (50, 60),
            (10, 40),
            (10, 60),
            (40, 60),
        }
        if not active_only:
            expected_edges.update({(2, 5), (3, 5), (20, 50), (30, 50)})

        assert set(graph.all_branches) == expected_edges

    def test_parallel_branches(self, graph, active_only):
        graph.add_branch(2, 5)
        assert graph.has_parallel_edges() is not active_only

        graph.add_branch(2, 3)
        assert graph.has_parallel_edges() is True

    def test_find_first_connected(self, graph):
        assert graph.find_first_connected(10, [20, 50]) == 20
