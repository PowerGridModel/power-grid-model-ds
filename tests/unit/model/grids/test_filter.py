# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds.utils import filter_downstream, filter_grid, filter_nodes, filter_path
from tests.fixtures.grid_classes import ExtendedGrid
from tests.fixtures.grids import build_basic_grid

# pylint: disable=missing-function-docstring


@pytest.fixture
def grid_with_feeders(basic_grid):
    basic_grid.set_feeder_ids()
    return basic_grid


def test_filter_returns_grid_instance(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    assert isinstance(result, Grid)


def test_filter_feeder_includes_all_feeder_nodes(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    visible = set(result.node.id.tolist())
    assert {102, 103, 106}.issubset(visible)


def test_filter_feeder_includes_substation_node(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    assert 101 in result.node.id.tolist()


def test_filter_feeder_excludes_nodes_from_other_feeders(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    visible = set(result.node.id.tolist())
    assert 104 not in visible
    assert 105 not in visible


def test_filter_feeder_includes_connecting_branches(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    assert 201 in result.line.id.tolist()
    assert 202 in result.line.id.tolist()
    assert 301 in result.transformer.id.tolist()
    assert 204 not in result.line.id.tolist()
    assert 601 not in result.link.id.tolist()


def test_filter_feeder_includes_appliances(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    assert 401 in result.sym_load.id.tolist()
    assert 402 in result.sym_load.id.tolist()
    assert 501 in result.source.id.tolist()
    assert 403 not in result.sym_load.id.tolist()
    assert 404 not in result.sym_load.id.tolist()


def test_filter_feeder_rebuilds_graphs(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201])
    assert result.graphs is not None
    assert result.graphs.complete_graph.external_to_internal(101) is not None
    assert result.graphs.complete_graph.external_to_internal(102) is not None


def test_filter_multiple_feeders(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[201, 204])
    assert set(result.node.id.tolist()) == {101, 102, 103, 104, 105, 106}


def test_filter_adjacent_nodes_expands_one_hop(grid_with_feeders):
    # Feeder 204 covers nodes 104, 105 + substation 101
    # With adjacent: also pull in nodes connected to 101, 104, 105
    result = filter_grid(grid_with_feeders, feeder_ids=[204], include_adjacent_nodes=True)
    visible = set(result.node.id.tolist())
    # Node 102 is adjacent to 101 (via line 201) → included
    assert 102 in visible
    # Node 104 and 105 are two hops from substation via feeder 201, but directly adjacent to 601
    assert 104 in visible
    assert 105 in visible


def test_filter_adjacent_nodes_includes_connecting_branches(grid_with_feeders):
    result = filter_grid(grid_with_feeders, feeder_ids=[204], include_adjacent_nodes=True)
    # Link 601 (104↔105) is within feeder 204
    assert 601 in result.link.id.tolist()
    # Line 201 (101↔102) becomes visible because 101 is in feeder 204 and 102 is one hop away
    assert 201 in result.line.id.tolist()


def test_filter_preserves_grid_subclass():
    extended = build_basic_grid(ExtendedGrid.empty())
    extended.set_feeder_ids()
    result = filter_grid(extended, feeder_ids=[201])
    assert type(result) is ExtendedGrid


# ---------------------------------------------------------------------------
# filter_path
# ---------------------------------------------------------------------------


def test_filter_path_returns_grid_instance(basic_grid):
    result = filter_path(basic_grid, start_node_id=102, end_node_id=106)
    assert isinstance(result, Grid)


def test_filter_path_direct_connection(basic_grid):
    # Transformer 301 connects 102 → 106 directly
    result = filter_path(basic_grid, start_node_id=102, end_node_id=106)
    assert set(result.node.id.tolist()) == {102, 106}
    assert 301 in result.transformer.id.tolist()


def test_filter_path_multi_hop(basic_grid):
    # 103-104 requires crossing the inactive gap: 103-202-102-201-101-204-105-601-104
    result = filter_path(basic_grid, start_node_id=103, end_node_id=104)
    assert {101, 102, 103, 104, 105}.issubset(set(result.node.id.tolist()))


def test_filter_path_same_node(basic_grid):
    result = filter_path(basic_grid, start_node_id=102, end_node_id=102)
    assert set(result.node.id.tolist()) == {102}


def test_filter_path_adjacent_nodes_expands_one_hop(basic_grid):
    # Path 102→103; adjacent should pull in 101 (via 201) and 106 (via transformer 301)
    result = filter_path(basic_grid, start_node_id=102, end_node_id=103, include_adjacent_nodes=True)
    visible = set(result.node.id.tolist())
    assert 101 in visible
    assert 106 in visible


# ---------------------------------------------------------------------------
# filter_nodes
# ---------------------------------------------------------------------------


def test_filter_nodes_returns_grid_instance(basic_grid):
    result = filter_nodes(basic_grid, node_ids=[102, 103])
    assert isinstance(result, Grid)


def test_filter_nodes_includes_only_specified_nodes(basic_grid):
    result = filter_nodes(basic_grid, node_ids=[102, 103])
    assert set(result.node.id.tolist()) == {102, 103}


def test_filter_nodes_includes_connecting_branches(basic_grid):
    result = filter_nodes(basic_grid, node_ids=[102, 103])
    assert 202 in result.line.id.tolist()


def test_filter_nodes_excludes_external_branches(basic_grid):
    # Line 201 connects 101↔102; 101 is not in the list
    result = filter_nodes(basic_grid, node_ids=[102, 103])
    assert 201 not in result.line.id.tolist()
    assert 301 not in result.transformer.id.tolist()


def test_filter_nodes_includes_appliances(basic_grid):
    result = filter_nodes(basic_grid, node_ids=[102, 103])
    assert 401 in result.sym_load.id.tolist()
    assert 402 in result.sym_load.id.tolist()
    assert 403 not in result.sym_load.id.tolist()


def test_filter_nodes_adjacent_nodes_expands_one_hop(basic_grid):
    # Starting from {102}: adjacent via 201→101, via 202→103, via transformer 301→106
    result = filter_nodes(basic_grid, node_ids=[102], include_adjacent_nodes=True)
    visible = set(result.node.id.tolist())
    assert 101 in visible
    assert 103 in visible
    assert 106 in visible


# ---------------------------------------------------------------------------
# filter_downstream
# ---------------------------------------------------------------------------


def test_filter_downstream_returns_grid_instance(basic_grid):
    result = filter_downstream(basic_grid, node_id=102)
    assert isinstance(result, Grid)


def test_filter_downstream_includes_node_itself(basic_grid):
    result = filter_downstream(basic_grid, node_id=102)
    assert 102 in result.node.id.tolist()


def test_filter_downstream_includes_downstream_nodes(basic_grid):
    # Downstream of 102 (away from substation 101): 102, 103, 106
    result = filter_downstream(basic_grid, node_id=102)
    assert {102, 103, 106}.issubset(set(result.node.id.tolist()))


def test_filter_downstream_excludes_upstream_nodes(basic_grid):
    result = filter_downstream(basic_grid, node_id=102)
    visible = set(result.node.id.tolist())
    assert 101 not in visible
    assert 104 not in visible
    assert 105 not in visible


def test_filter_downstream_adjacent_nodes_adds_upstream(basic_grid):
    # Downstream of 102 = {102, 103, 106}; adjacent expansion adds 101 (one hop upstream)
    result = filter_downstream(basic_grid, node_id=102, include_adjacent_nodes=True)
    assert 101 in result.node.id.tolist()
