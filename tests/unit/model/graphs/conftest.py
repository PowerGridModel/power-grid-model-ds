# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from copy import deepcopy

import pytest

from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel


@pytest.fixture(name="graph_with_5_nodes")
def fixture_graph_with_5_nodes(graph: BaseGraphModel):
    """Return a graph with 2 routes"""
    graph = deepcopy(graph)
    for node_id in range(1, 6):
        graph.add_node(node_id)
    return graph


@pytest.fixture
def graph_with_2_routes(graph_with_5_nodes: BaseGraphModel):
    """Return a graph with 2 routes"""
    graph_with_5_nodes.add_branch(1, 2)  # Route 1
    graph_with_5_nodes.add_branch(2, 3)  # Route 1
    graph_with_5_nodes.add_branch(1, 5)  # Route 2
    graph_with_5_nodes.add_branch(5, 4)  # Route 2
    return graph_with_5_nodes
