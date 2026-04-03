# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from collections import Counter

import rustworkx as rx


def find_fundamental_cycles_rustworkx(graph):
    """Detect fundamental cycles in the graph and returns the node cycle paths.

    The nodes in cycles are found by:
    1. Creating a minimum spanning forest (MSF) of the (possibly disconnected) graph, which is a set of minimum
    spanning trees (MST's). Here, a MST is a subset of the original graph that connects all nodes with the minimum
    possible amount of edges. (Also, see https://mathworld.wolfram.com/SpanningTree.html).

    For a connected graph, all nodes are connected by edges, leading to a single MST. In that case,
    the MSF consists of a single MST. (See https://mathworld.wolfram.com/ConnectedGraph.html for more information).

    For a disconnected graph, there are multiple separated subgraphs; in other words, not all nodes are connected.
    (ALso, see https://mathworld.wolfram.com/DisconnectedGraph.html). Each of the subgraphs will then form a MST.
    The MSF is then the collection of these MST's.

    NOTE: If there are cycles in the graph, the MSF is not unique. One of the options will be chosen.
    Regardless of the chosen MSF, the algorithm works.

    2. Determining which edges in the original graph are not part of the MSF. A propery of MST's is that adding
    a single edge between nodes will always form a cycle.

    3. Looping through the unused edges and determining the path of nodes of the cycle it would form.
    This is done by determining the shortest path between the nodes on both sides of an unused edge within the MSF.
    A combination of this shortest path and the unused edge forms the cycle path. A list of these paths is returned.

    Returns:
        node_cycle_paths(list[list[[int]]): a list of node paths, which are each a list of node_ids in a path.
    """
    mst = rx.minimum_spanning_tree(graph)
    unused_edges = _find_unused_edges_rustworkx(graph, mst)
    return _get_cycle_paths_rustworkx(unused_edges, mst)  # node cycle paths


def _find_unused_edges_rustworkx(full_graph, subset_graph):
    """Determine unused edges by comparing all edges with a subset of edges in the MST."""
    full_edges = Counter(full_graph.edge_list())
    subset_edges = Counter(subset_graph.edge_list())
    return full_edges - subset_edges  # unused edges


def _get_cycle_paths_rustworkx(unused_edges, spanning_forest_graph):
    """Find nodes that are part of a cycle in the graph using the MST."""
    node_cycle_paths = []
    for source, target in unused_edges:
        path_mapping = rx.dijkstra_shortest_paths(spanning_forest_graph, source, target, weight_fn=lambda _: 1)

        path_nodes = list(path_mapping[target])
        path_nodes.append(source)

        node_cycle_paths.append(path_nodes)
    return node_cycle_paths
