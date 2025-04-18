# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""
Test for Generator Data Source
"""

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.line import LineGenerator
from power_grid_model_ds._core.data_source.generator.arrays.node import NodeGenerator
from power_grid_model_ds._core.data_source.generator.arrays.source import SourceGenerator
from power_grid_model_ds._core.data_source.generator.grid_generators import RadialGridGenerator
from power_grid_model_ds._core.load_flow import PowerGridModelInterface
from power_grid_model_ds._core.model.arrays import LineArray, NodeArray, SourceArray, SymLoadArray
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid


def test_generate_random_grid():
    """Generate a random grid with correct structure"""
    grid_generator = RadialGridGenerator(grid_class=Grid)
    grid = grid_generator.run(seed=0)

    # All nodes should be in both graphs
    assert len(grid.graphs.active_graph.external_ids) == len(grid.node)
    assert len(grid.graphs.complete_graph.external_ids) == len(grid.node)

    assert 102 == len(grid.node)
    assert 2 == len(grid.source)
    assert 100 == len(grid.sym_load)

    inactive_mask = np.logical_or(grid.line.from_status == 0, grid.line.to_status == 0)
    inactive_lines = grid.line[inactive_mask]
    assert 10 == len(inactive_lines)
    assert len(grid.line) - 10 == grid.graphs.active_graph.nr_branches
    assert len(grid.line) == grid.graphs.complete_graph.nr_branches


def test_graph_generate_random_grid_with_different_graph_engines(graph: BaseGraphModel):
    """Generate a random grid with correct structure"""
    grid_generator = RadialGridGenerator(grid_class=Grid, graph_model=graph.__class__)
    grid = grid_generator.run(seed=0)
    assert isinstance(grid.graphs.active_graph, graph.__class__)


def test_generate_random_nodes(grid: Grid):
    """Generate random nodes"""
    node_generator = NodeGenerator(grid, seed=0)
    nodes, loads_low, loads_high = node_generator.run(amount=2)

    # We have generated 2 nodes with load scenarios
    assert 2 == len(nodes)
    assert 2 == len(loads_low)
    assert 2 == len(loads_high)

    # The arrays are of the correct type
    assert isinstance(nodes, NodeArray)
    assert isinstance(loads_low, SymLoadArray)
    assert isinstance(loads_high, SymLoadArray)

    # All loads are coupled to a node in the nodes array
    assert all(np.isin(loads_high.node, nodes.id))
    assert all(np.isin(loads_low.node, nodes.id))


def test_generate_random_sources(grid: Grid):
    """Generate random sources"""
    source_generator = SourceGenerator(grid=grid, seed=0)
    nodes, sources = source_generator.run(amount=1)

    # We have generated 1 nodes with load scenarios
    assert 1 == len(nodes)
    assert 1 == len(sources)

    # The arrays are of the correct type
    assert isinstance(nodes, NodeArray)
    assert isinstance(sources, SourceArray)

    # All sources are coupled to a node in the nodes array
    assert all(np.isin(sources.node, nodes.id))


def test_generate_random_lines(grid: Grid):
    """Generate random lines"""
    nodes = NodeArray.zeros(4)
    nodes.id = [0, 1, 2, 3]
    nodes.u_rated = [10_500] * 4

    sources = SourceArray.zeros(1)
    sources.id = [4]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    grid.append(nodes)
    grid.append(sources)

    line_generator = LineGenerator(grid=grid, seed=0)
    lines = line_generator.run(amount=2)

    # We have generated at least 5 lines
    assert len(lines) >= 5
    # Two lines are inactive
    inactive_line_mask = np.logical_or(lines.from_status == 0, lines.to_status == 0)
    assert 2 == sum(inactive_line_mask)

    assert isinstance(lines, LineArray)

    # All lines have from and to nodes in the nodes array
    assert all(np.isin(lines.from_node, nodes.id))
    assert all(np.isin(lines.to_node, nodes.id))


def test_create_routes(grid: Grid):
    """Generate new routes"""
    nodes = NodeArray.zeros(4)
    nodes.id = [0, 1, 2, 3]
    nodes.u_rated = [10_500] * 4

    sources = SourceArray.zeros(1)
    sources.id = [4]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    grid.append(nodes)
    grid.append(sources)

    line_generator = LineGenerator(grid=grid, seed=0)
    assert 0 == len(line_generator.line_array)
    line_generator.create_routes(2)

    # We have generated 2 lines
    assert 2 == len(line_generator.line_array)
    # These lines are active
    inactive_line_mask = np.logical_or(
        line_generator.line_array.from_status == 0,
        line_generator.line_array.to_status == 0,
    )
    assert 0 == sum(inactive_line_mask)

    # All lines have from node in sources.node
    assert all(np.isin(line_generator.line_array.from_node, sources.node))
    # All lines have to node in nodes.id
    assert all(np.isin(line_generator.line_array.to_node, nodes.id))


def test_determine_number_of_routes(grid: Grid):
    """Number of routes"""
    line_generator = LineGenerator(grid=grid, seed=0)

    line_generator.grid.node = NodeArray.zeros(4)
    line_generator.grid.source = SourceArray.zeros(1)

    # The number of routes has a minimum of 1
    number_of_routes = line_generator.determine_number_of_routes()
    assert 1 == number_of_routes

    # The number of routes should be increased based on the number of sources
    line_generator.grid.source = SourceArray.zeros(2)
    number_of_routes = line_generator.determine_number_of_routes()
    assert 2 == number_of_routes

    # When more nodes are added the number of routes increases
    line_generator.grid.node = NodeArray.zeros(50)
    number_of_routes = line_generator.determine_number_of_routes()
    assert 3 == number_of_routes


def test_connect_nodes(grid: Grid):
    """Connect nodes"""
    nodes = NodeArray.zeros(4)
    nodes.id = [0, 1, 2, 3]
    nodes.u_rated = [10_500] * 4

    sources = SourceArray.zeros(1)
    sources.id = [4]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    line_array = LineArray.zeros(1)
    line_array.id = [5]
    line_array.from_node = [0]
    line_array.to_node = [1]
    line_array.from_status = [1]
    line_array.to_status = [1]

    grid.append(nodes)
    grid.append(sources)
    grid.append(line_array)

    line_generator = LineGenerator(grid=grid, seed=0)
    line_generator.line_array = line_array

    line_generator.set_unconnected_nodes()

    assert [0, 1] == line_generator.connected_nodes
    assert [2, 3] == line_generator.unconnected_nodes

    line_generator.connect_nodes()

    # We have generated 1 extra line
    assert 2 == len(line_generator.line_array)


def test_create_nops(grid: Grid):
    """Create normally open points"""
    nodes = NodeArray.zeros(4)
    nodes.id = [0, 1, 2, 3]
    nodes.u_rated = [10_500] * 4

    sources = SourceArray.zeros(1)
    sources.id = [4]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    line_array = LineArray.zeros(2)
    line_array.id = [5, 6]
    line_array.from_node = [0, 0]
    line_array.to_node = [1, 2]
    line_array.from_status = [1, 1]
    line_array.to_status = [1, 1]

    grid.append(nodes)
    grid.append(sources)
    grid.append(line_array)

    line_generator = LineGenerator(grid=grid, seed=0)
    line_generator.line_array = line_array

    line_generator.create_nop_lines(1)

    # We have generated 1 extra line
    assert 3 == len(line_generator.line_array)
    # This line is inactive
    inactive_line_mask = np.logical_or(
        line_generator.line_array.from_status == 0,
        line_generator.line_array.to_status == 0,
    )
    assert 1 == sum(inactive_line_mask)


def test_generate_random_grid_with_tranformers():
    """Generate a random grid with correct structure"""
    grid_generator = RadialGridGenerator(grid_class=Grid)
    grid = grid_generator.run(seed=0, create_10_3_kv_net=True)

    # two ten to 3 kv transformers have been added
    assert 2 == len(grid.transformer)
    assert all(np.isclose([10_500] * 2, grid.transformer.u1.tolist()))
    assert all(np.isclose([3_000] * 2, grid.transformer.u2.tolist()))

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    core_interface.calculate_power_flow()
