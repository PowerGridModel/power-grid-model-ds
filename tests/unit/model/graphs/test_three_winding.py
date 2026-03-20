import pytest

from power_grid_model_ds._core.model.arrays.pgm_arrays import NodeArray, ThreeWindingTransformerArray
from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel


def _setup_graph(graph: RustworkxGraphModel) -> None:
    nodes = NodeArray.empty(12)
    nodes.id = [1, 2, 3, 4, 5, 6, 10, 20, 30, 40, 50, 60]

    graph.add_node_array(nodes)

    # The three winding arrays are open at 5 and 50.
    # TODO: add all the 10-60 and 10-40 as well.
    #                            -------------------
    #                            |                 |
    # 1 -- 2 --- 3 -- 4         10 -- 20 --- 30 -- 40
    #         |                  |        |        |
    #         5                  |        50       |
    #         |                  |        |        |
    #         6                  ---------60--------

    three = ThreeWindingTransformerArray.empty(2)
    three.node_1 = [2, 20]
    three.node_2 = [3, 30]
    three.node_3 = [5, 50]
    three.status_1 = [1, 1]
    three.status_2 = [1, 1]
    three.status_3 = [0, 0]
    graph.add_branch3_array(three)

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
def graph(active_only):
    return _setup_graph(RustworkxGraphModel(active_only=active_only))


def list_of_paths_to_set(paths, ordered_paths=False):
    if ordered_paths:
        return {tuple(path) for path in paths}
    else:
        return {tuple(sorted(path)) for path in paths}


@pytest.mark.usefixtures("graph")
class TestThreeWindingTransformer:
    def test_three_winding_transformer_group(self, graph, active_only):
        expected = set() if active_only else {(2, 3, 5), (20, 30, 50)}
        assert graph._three_winding_branch_groups == expected

        with graph.tmp_remove_branches([(2, 3), (20, 30)]):
            assert graph._three_winding_branch_groups == expected

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

        assert {tuple(path) for path in actual_paths} == expected

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

        assert {tuple(path) for path in actual_paths} == expected

    def test_nr_branches(self, graph, active_only):
        expected = 11 if active_only else 15
        assert graph.nr_branches == expected

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

    def test_find_first_connected(self, graph, active_only):
        assert graph.find_first_connected(10, [20, 50]) == 20
