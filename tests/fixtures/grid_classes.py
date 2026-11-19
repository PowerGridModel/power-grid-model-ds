# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass
from typing import ClassVar, Self

import numpy as np
from numpy._typing import NDArray

from power_grid_model_ds import FancyArray
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import CustomLineArray, CustomNodeArray, DefaultedCustomLineArray, DefaultedCustomNodeArray
from tests.fixtures.graph_models import CustomTestGraphModel


class UserDefinedArray(FancyArray):
    """A user defined array that does not inherit from any existing grid array with id references."""

    branch_id: NDArray[np.int32]
    node_id: NDArray[np.int32]

    _id_columns: ClassVar[set[str]] = {"branch_id", "node_id"}
    _defaults: ClassVar[dict[str, int]] = {"branch_id": 42, "node_id": 43}


@dataclass(repr=False)
class ExtendedGrid(Grid):
    """ExtendedGrid class for testing purposes."""

    node: DefaultedCustomNodeArray
    line: DefaultedCustomLineArray
    user_defined: UserDefinedArray
    extra_value: int = 123


class ExtendedGraphContainer(GraphContainer):
    """Graph container type used by ExtendedGraphGrid."""


@dataclass(repr=False)
class ExtendedGraphGrid(Grid):
    """Grid using a custom graph container and graph model."""

    graphs: ExtendedGraphContainer
    extra_value: int = 123

    @classmethod
    def empty(cls: type[Self], graph_model: type[BaseGraphModel] = CustomTestGraphModel) -> Self:
        empty_fields = cls._get_empty_fields()
        empty_fields["graphs"] = ExtendedGraphContainer.empty(graph_model=graph_model)
        return cls(**empty_fields)


@dataclass(repr=False)
class ExtendedGridNoDefaults(Grid):
    node: CustomNodeArray
    line: CustomLineArray
