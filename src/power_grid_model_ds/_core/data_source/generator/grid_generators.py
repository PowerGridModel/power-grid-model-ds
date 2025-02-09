# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generators for the grid"""

from typing import Generic, Type, TypeVar

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.line import LineGenerator
from power_grid_model_ds._core.data_source.generator.arrays.node import NodeGenerator
from power_grid_model_ds._core.data_source.generator.arrays.source import SourceGenerator
from power_grid_model_ds._core.data_source.generator.arrays.transformer import TransformerGenerator
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel
from power_grid_model_ds._core.model.grids.base import Grid

# pylint: disable=too-few-public-methods,too-many-arguments,too-many-positional-arguments

T = TypeVar("T", bound=Grid)


class RadialGridGenerator(Generic[T]):
    """Generates a random but structurally correct radial grid with the given specifications"""

    def __init__(
        self,
        grid_class: Type[T],
        nr_nodes: int = 100,
        nr_sources: int = 2,
        nr_nops: int = 10,
        graph_model: type[BaseGraphModel] = RustworkxGraphModel,
    ):
        self.grid_class = grid_class
        self.graph_model = graph_model
        self.nr_nodes = nr_nodes
        self.nr_sources = nr_sources
        self.nr_nops = nr_nops

    def run(self, seed=None, create_10_3_kv_net: bool = False) -> T:
        """Run the generator to create a random radial grid.

        if a seed is provided, this will be used to set rng.
        """
        grid = self.grid_class.empty(graph_model=self.graph_model)

        # create nodeArray
        node_generator = NodeGenerator(grid=grid, seed=seed)

        nodes, _loads_low, loads_high = node_generator.run(amount=self.nr_nodes)
        grid.append(nodes)
        grid.append(loads_high)

        # create sourceArray
        source_generator = SourceGenerator(grid=grid, seed=seed)
        nodes, sources = source_generator.run(amount=self.nr_sources)
        grid.append(nodes)
        grid.append(sources)

        # create lineArray
        line_generator = LineGenerator(grid=grid, seed=seed)
        lines = line_generator.run(amount=self.nr_nops)
        grid.append(lines)

        if create_10_3_kv_net:
            # create 3kV nodes
            nodes, _loads_low, _loads_high = node_generator.run(amount=10, voltage_level=3_000)
            grid.append(nodes)
            grid.append(_loads_high)

            # create transformerArray
            transformer_generator = TransformerGenerator(grid=grid, seed=seed)
            transformers = transformer_generator.run(amount=2)
            grid.append(transformers)

            lines = line_generator.run(amount=0, number_of_routes=0)
            grid.append(lines[~np.isin(lines.id, grid.line.id)])

        return grid
