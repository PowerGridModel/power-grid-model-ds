# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Arrays"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.fancypy import concatenate
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.dtypes.appliances import Source, SymGen, SymLoad
from power_grid_model_ds._core.model.dtypes.branches import (
    Branch,
    Branch3,
    Line,
    Link,
    ThreeWindingTransformer,
    Transformer,
)
from power_grid_model_ds._core.model.dtypes.id import Id
from power_grid_model_ds._core.model.dtypes.nodes import Node
from power_grid_model_ds._core.model.dtypes.regulators import TransformerTapRegulator
from power_grid_model_ds._core.model.dtypes.sensors import AsymVoltageSensor, SymPowerSensor, SymVoltageSensor

# pylint: disable=missing-class-docstring


class IdArray(Id, FancyArray):
    pass


class SymLoadArray(IdArray, SymLoad):
    pass


class SymGenArray(IdArray, SymGen):
    pass


class SourceArray(IdArray, Source):
    pass


class NodeArray(IdArray, Node):
    pass


class BranchArray(IdArray, Branch):
    @property
    def node_ids(self):
        """Return both from_node and to_node in one array"""
        return np.concatenate([self.data["from_node"], self.data["to_node"]])

    @property
    def is_active(self) -> NDArray[np.bool_]:
        """Returns boolean whether branch is closed at both ends"""
        return np.logical_and(self.from_status == 1, self.to_status == 1)

    def filter_parallel(self, n_parallel: int, mode: Literal["eq", "neq"]) -> "BranchArray":
        """Return branches that have n_parallel connections.

        Args:
            branches: BranchArray.
            n_parallel: the number of connections between the same nodes
            mode: mode of comparison. "eq" (equal) or "neq" (non-equal).

        Returns:
            - when n_parallel is 1 and mode is 'eq', the function returns branches that are not parallel.
            - when n_parallel is 1 and mode is 'neq', the function returns branches that are parallel.
        """
        _, index, counts = np.unique(self[["from_node", "to_node"]], return_counts=True, return_index=True)

        match mode:
            case "eq":
                counts_mask = counts == n_parallel
            case "neq":
                counts_mask = counts != n_parallel
            case _:
                raise ValueError(f"mode {mode} not supported")

        if mode == "eq" and n_parallel == 1:
            return self[index][counts_mask]
        filtered_branches = self[index][counts_mask]
        return self.filter(from_node=filtered_branches.from_node, to_node=filtered_branches.to_node)


class LinkArray(Link, BranchArray):
    pass


class LineArray(Line, BranchArray):
    pass


class TransformerArray(Transformer, BranchArray):
    pass


class Branch3Array(IdArray, Branch3):
    def as_branches(self) -> BranchArray:
        """Convert Branch3Array to BranchArray."""
        branches_1_2 = BranchArray.empty(self.size)
        branches_1_2.from_node = self.node_1
        branches_1_2.to_node = self.node_2
        branches_1_2.from_status = self.status_1
        branches_1_2.to_status = self.status_2

        branches_1_3 = BranchArray.empty(self.size)
        branches_1_3.from_node = self.node_1
        branches_1_3.to_node = self.node_3
        branches_1_3.from_status = self.status_1
        branches_1_3.to_status = self.status_3

        branches_2_3 = BranchArray.empty(self.size)
        branches_2_3.from_node = self.node_2
        branches_2_3.to_node = self.node_3
        branches_2_3.from_status = self.status_2
        branches_2_3.to_status = self.status_3
        return concatenate(branches_1_2, branches_1_3, branches_2_3)


class ThreeWindingTransformerArray(Branch3Array, ThreeWindingTransformer):
    pass


class TransformerTapRegulatorArray(IdArray, TransformerTapRegulator):
    pass


class SymPowerSensorArray(IdArray, SymPowerSensor):
    pass


class SymVoltageSensorArray(IdArray, SymVoltageSensor):
    pass


class AsymVoltageSensorArray(IdArray, AsymVoltageSensor):
    pass
