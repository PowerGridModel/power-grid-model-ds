# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generator for LineArray"""

import numpy as np

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.data_source.generator.arrays.base import BaseGenerator
from power_grid_model_ds._core.model.arrays import LineArray, TransformerArray
from power_grid_model_ds._core.model.grids.base import Grid

AVERAGE_ROUTE_SIZE = 20


class LineGenerator(BaseGenerator):
    """Generator for line elements in the grid"""

    def __init__(self, grid: Grid, seed: int) -> None:
        super().__init__(grid=grid, seed=seed)
        self.connected_nodes: list = []
        self.unconnected_nodes: list = []
        self.line_array: LineArray = self.grid.line.__class__()
        self.trafo_array: TransformerArray = self.grid.transformer.__class__()

    # pylint: disable=arguments-differ
    def run(self, amount: int, number_of_routes: int | None = None) -> LineArray:
        """Generate routes, lines and normally open points (NOPs)"""

        self.trafo_array = self.grid.transformer
        if number_of_routes is None:
            number_of_routes = self.determine_number_of_routes()
        if number_of_routes > 0:
            self.create_routes(number_of_routes)
        else:
            self.line_array = self.grid.line

        # while not all connected, add lines from a connected node to an unconnected node
        self.set_unconnected_nodes()
        while any(self.unconnected_nodes):
            self.connect_nodes()
            self.set_unconnected_nodes()

        number_of_nops = amount
        if number_of_nops > 0:
            self.create_nop_lines(number_of_nops)

        return self.line_array

    def create_routes(self, number_of_routes: int):
        """Create a number of lines from the substation to unconnected nodes"""
        # each source should have at least one route
        number_of_sources = len(self.grid.source)
        from_nodes = self.rng.choice(self.grid.source["node"], number_of_routes - number_of_sources, replace=True)
        not_source_mask = ~np.isin(self.grid.node["id"], self.grid.source["node"])
        to_nodes = self.rng.choice(self.grid.node["id"][not_source_mask], number_of_routes, replace=False)
        capacities = 100 + self.rng.exponential(200, number_of_routes)
        line_array = self.grid.line.__class__.zeros(number_of_routes)
        line_array["id"] = 1 + self.grid.max_id + np.arange(number_of_routes)
        line_array["from_node"] = np.concatenate((self.grid.source["node"], from_nodes))
        line_array["to_node"] = to_nodes
        line_array["from_status"] = [1] * number_of_routes
        line_array["to_status"] = [1] * number_of_routes
        line_array["r1"] = self.rng.exponential(0.2, number_of_routes)
        line_array["x1"] = self.rng.exponential(0.02, number_of_routes)
        line_array["i_n"] = capacities
        self.line_array = line_array

    def determine_number_of_routes(self) -> int:
        """Decide on a number of routes based on expected route-size"""
        expected_number_of_routes = int(np.ceil(len(self.grid.node) / AVERAGE_ROUTE_SIZE))
        number_of_sources = len(self.grid.source)
        # The number of routes is the max of the number of sources
        # and the expected number based on size
        return max(expected_number_of_routes, number_of_sources)

    def connect_nodes(self):
        """Add a new line between an active and inactive line"""
        to_node = self.rng.choice(self.unconnected_nodes)
        to_voltage = self.grid.node.data[self.grid.node["id"] == to_node]["u_rated"][0]
        same_voltage_mask = self.grid.node["u_rated"] == to_voltage
        same_voltage_nodes = self.grid.node.data[same_voltage_mask]
        options_mask = np.isin(self.connected_nodes, same_voltage_nodes["id"])
        from_node = self.rng.choice(np.array(self.connected_nodes)[options_mask])
        capacity = 100 + self.rng.exponential(200, 1)
        new_line = self.grid.line.__class__.zeros(1)
        new_line["id"] = 1 + max(max(self.line_array["id"]), self.grid.max_id)  # pylint: disable=nested-min-max
        new_line["from_node"] = from_node
        new_line["to_node"] = to_node
        new_line["from_status"] = [1]
        new_line["to_status"] = [1]
        new_line["r1"] = self.rng.exponential(0.2, 1)
        new_line["x1"] = self.rng.exponential(0.02, 1)
        new_line["i_n"] = capacity
        self.line_array = fp.concatenate(self.line_array, new_line)

    def create_nop_lines(self, number_of_nops: int):
        """Create the inactive lines between different routes (Normally Open Points)"""
        nops = [self.rng.choice(self.grid.node["id"], 2, replace=False) for _ in range(number_of_nops)]
        from_nodes = [nop[0] for nop in nops]
        to_nodes = [nop[1] for nop in nops]
        capacities = 100 + self.rng.exponential(200, number_of_nops)
        nop_lines = self.grid.line.__class__.zeros(number_of_nops)
        nop_lines["id"] = 1 + self.line_array["id"].max() + np.arange(number_of_nops)
        nop_lines["from_node"] = from_nodes
        nop_lines["to_node"] = to_nodes
        nop_lines["from_status"] = [1] * number_of_nops
        nop_lines["to_status"] = [0] * number_of_nops
        nop_lines["r1"] = self.rng.exponential(0.2, number_of_nops)
        nop_lines["x1"] = self.rng.exponential(0.02, number_of_nops)
        nop_lines["i_n"] = capacities
        self.line_array = fp.concatenate(self.line_array, nop_lines)

    def set_unconnected_nodes(self) -> None:
        """From a line array and total set of nodes determine which are not yet connected"""
        connected_link_mask = np.logical_or(
            np.isin(self.grid.node["id"], self.line_array["from_node"]),
            np.isin(self.grid.node["id"], self.line_array["to_node"]),
        )
        connected_trafo_mask = np.logical_or(
            np.isin(self.grid.node["id"], self.trafo_array["from_node"]),
            np.isin(self.grid.node["id"], self.trafo_array["to_node"]),
        )
        connected_mask = np.logical_or(
            connected_link_mask,
            connected_trafo_mask,
        )
        connected_nodes = self.grid.node["id"][connected_mask]
        unconnected_nodes = self.grid.node["id"][~connected_mask]

        self.unconnected_nodes = unconnected_nodes.tolist()
        self.connected_nodes = connected_nodes.tolist()
