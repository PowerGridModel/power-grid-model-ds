# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from power_grid_model_ds._core.model.arrays import NodeArray, ThreeWindingTransformerArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.graphs.container import GraphContainer

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

    basic_grid.graphs.active_graph.has_branch(1000, 1002)
    basic_grid.graphs.active_graph.has_branch(1001, 1002)

    assert basic_grid.graphs.active_graph.nr_nodes == graphs.active_graph.nr_nodes
    assert basic_grid.graphs.active_graph.nr_branches == 5 + 1

    basic_grid.graphs.active_graph.has_branch(1000, 1001)
    assert not basic_grid.graphs.active_graph.has_branch(1000, 1002)
    assert not basic_grid.graphs.active_graph.has_branch(1001, 1002)


def test_from_arrays_invalid_arrays(basic_grid):
    basic_grid.node = basic_grid.node.exclude(id=106)

    with pytest.raises(RecordDoesNotExist):
        GraphContainer.from_arrays(basic_grid)
