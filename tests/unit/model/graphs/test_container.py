# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from power_grid_model_ds._core.model.arrays import NodeArray, ThreeWindingTransformerArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.errors import GraphError

# pylint: disable=missing-function-docstring


def test_from_arrays(basic_grid):
    graphs = GraphContainer.from_arrays(basic_grid)

    assert isinstance(graphs, GraphContainer)
    assert basic_grid.graphs.complete_graph.nr_nodes == graphs.complete_graph.nr_nodes
    assert basic_grid.graphs.complete_graph.nr_branches == 6

    assert basic_grid.graphs.active_graph.nr_nodes == graphs.active_graph.nr_nodes
    assert basic_grid.graphs.active_graph.nr_branches == 5

    assert set(basic_grid.node.id) == set(graphs.active_graph.external_ids)
    assert set(basic_grid.node.id) == set(graphs.complete_graph.external_ids)


@pytest.fixture
def graph_container_with_5_nodes():
    graph_container = GraphContainer.empty()
    for node_id in range(1, 6):
        node = NodeArray.empty(1)
        node.id = node_id
        graph_container.add_node(node)
    return graph_container


@pytest.fixture
def three_winding_transformers():
    three_winding_transformers = ThreeWindingTransformerArray.empty(2)
    three_winding_transformers.id = [301, 302]
    three_winding_transformers.node_1 = [1, 1]
    three_winding_transformers.node_2 = [2, 4]
    three_winding_transformers.node_3 = [3, 5]
    three_winding_transformers.status_1 = [1, 1]
    three_winding_transformers.status_2 = [1, 1]
    three_winding_transformers.status_3 = [0, 1]

    return three_winding_transformers


def test_add_branch3(graph_container_with_5_nodes, three_winding_transformers):
    graph_container_with_5_nodes.add_branch3(three_winding_transformers)
    for from_node, to_node in [(1, 2), (1, 4), (1, 5), (4, 5)]:
        assert graph_container_with_5_nodes.active_graph.has_branch(from_node, to_node)
        assert graph_container_with_5_nodes.complete_graph.has_branch(from_node, to_node)

    for from_node, to_node in [(1, 3), (2, 3)]:
        assert not graph_container_with_5_nodes.active_graph.has_branch(from_node, to_node)
        assert graph_container_with_5_nodes.complete_graph.has_branch(from_node, to_node)


def test_delete_branch3(graph_container_with_5_nodes, three_winding_transformers):
    graph_container_with_5_nodes.add_branch3(three_winding_transformers)
    graph_container_with_5_nodes.delete_branch3(three_winding_transformers[0])

    assert not graph_container_with_5_nodes.active_graph.has_branch(1, 2)
    assert not graph_container_with_5_nodes.complete_graph.has_branch(1, 2)
    for from_node, to_node in [(1, 4), (1, 5), (4, 5)]:
        assert graph_container_with_5_nodes.active_graph.has_branch(from_node, to_node)
        assert graph_container_with_5_nodes.complete_graph.has_branch(from_node, to_node)
    graph_container_with_5_nodes.delete_branch3(three_winding_transformers[1])

    for from_node, to_node in [(1, 2), (1, 4), (1, 5), (4, 5)]:
        assert not graph_container_with_5_nodes.active_graph.has_branch(from_node, to_node)
        assert not graph_container_with_5_nodes.complete_graph.has_branch(from_node, to_node)


def test_from_arrays_active_three_winding(basic_grid):
    nodes = NodeArray.zeros(3)
    nodes.id = [1000, 1001, 1002]
    basic_grid.append(nodes)

    three_winding_transformer = ThreeWindingTransformerArray.zeros(1)
    three_winding_transformer.node_1 = 1000
    three_winding_transformer.node_2 = 1001
    three_winding_transformer.node_3 = 1002
    three_winding_transformer.status_1 = 1
    three_winding_transformer.status_2 = 1
    three_winding_transformer.status_3 = 1
    basic_grid.append(three_winding_transformer)

    graphs = GraphContainer.from_arrays(basic_grid)
    assert basic_grid.graphs.complete_graph.nr_nodes == graphs.complete_graph.nr_nodes
    assert basic_grid.graphs.complete_graph.nr_branches == 6 + 3

    assert basic_grid.graphs.active_graph.nr_nodes == graphs.active_graph.nr_nodes
    assert basic_grid.graphs.active_graph.nr_branches == 5 + 3


def test_from_arrays_partially_active_three_winding(basic_grid):
    nodes = NodeArray.zeros(3)
    nodes.id = [1000, 1001, 1002]
    basic_grid.append(nodes)

    three_winding_transformer = ThreeWindingTransformerArray.zeros(1)
    three_winding_transformer.node_1 = 1000
    three_winding_transformer.node_2 = 1001
    three_winding_transformer.node_3 = 1002
    three_winding_transformer.status_1 = 1
    three_winding_transformer.status_2 = 1
    three_winding_transformer.status_3 = 0
    basic_grid.append(three_winding_transformer)

    graphs = GraphContainer.from_arrays(basic_grid)
    assert basic_grid.graphs.complete_graph.nr_nodes == graphs.complete_graph.nr_nodes
    assert basic_grid.graphs.complete_graph.nr_branches == 6 + 3

    # Implicitly test that the correct branches are added
    # Current implementation does not have a has_branch method.
    basic_grid.graphs.complete_graph.delete_branch(1000, 1001)
    basic_grid.graphs.complete_graph.delete_branch(1000, 1002)
    basic_grid.graphs.complete_graph.delete_branch(1001, 1002)

    assert basic_grid.graphs.active_graph.nr_nodes == graphs.active_graph.nr_nodes
    assert basic_grid.graphs.active_graph.nr_branches == 5 + 1

    # Implicitly test that the correct branches are added
    # Current implementation does not have a has_branch method.
    basic_grid.graphs.active_graph.delete_branch(1000, 1001)
    with pytest.raises(GraphError):
        basic_grid.graphs.active_graph.delete_branch(1000, 1002)

    with pytest.raises(GraphError):
        basic_grid.graphs.active_graph.delete_branch(1001, 1002)


def test_from_arrays_invalid_arrays(basic_grid):
    basic_grid.node = basic_grid.node.exclude(id=106)

    with pytest.raises(RecordDoesNotExist):
        GraphContainer.from_arrays(basic_grid)
