# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Stores the GraphContainer class"""

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator

import numpy as np

from power_grid_model_ds._core.model.arrays import Branch3Array, BranchArray, NodeArray
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid


@dataclass
class GraphContainer:
    """Contains graphs"""

    active_graph: BaseGraphModel
    """The graph containing only active branches."""

    complete_graph: BaseGraphModel
    """The graph containing all branches."""

    @property
    def graph_attributes(self) -> Generator:
        """Get all graph attributes of the container.

        Yield:
            BaseGraphModel: The next graph attribute.
        """
        return (field for field in dataclasses.fields(self) if isinstance(getattr(self, field.name), BaseGraphModel))

    @classmethod
    def empty(cls, graph_model: type[BaseGraphModel] = RustworkxGraphModel) -> "GraphContainer":
        """Get empty instance of GraphContainer.

        Args:
            graph_model (type[BaseGraphModel]): The graph model to use. Defaults to RustworkxGraphModel.
              An alternative graph model can be passed as an argument.

        Returns:
            GraphContainer: The empty graph container.
        """

        return cls(
            active_graph=graph_model(active_only=True),
            complete_graph=graph_model(active_only=False),
        )

    def add_node_array(self, node_array: NodeArray) -> None:
        """Add a node to all graphs"""
        for field in dataclasses.fields(self):
            graph = getattr(self, field.name)
            graph.add_node_array(node_array=node_array, raise_on_fail=False)

    def add_branch_array(self, branch_array: BranchArray) -> None:
        """Add a branch to all graphs"""
        for field in self.graph_attributes:
            graph = getattr(self, field.name)
            graph.add_branch_array(branch_array=branch_array)

    def add_branch3_array(self, branch3_array: Branch3Array) -> None:
        """Add a branch to all graphs"""
        for field in self.graph_attributes:
            graph = getattr(self, field.name)
            graph.add_branch3_array(branch3_array=branch3_array)

    def delete_node(self, node: NodeArray) -> None:
        """Remove a node from all graphs"""
        for field in dataclasses.fields(self):
            graph = getattr(self, field.name)
            graph.delete_node_array(node_array=node)

    def delete_branch(self, branch: BranchArray) -> None:
        """Remove a branch from all graphs"""
        for field in self.graph_attributes:
            graph = getattr(self, field.name)
            graph.delete_branch_array(branch_array=branch)

    def delete_branch3(self, branch: Branch3Array) -> None:
        """Remove a branch from all graphs"""
        for field in self.graph_attributes:
            graph = getattr(self, field.name)
            graph.delete_branch3_array(branch3_array=branch)

    def make_active(self, branch: BranchArray) -> None:
        """Add branch to all active_only graphs"""

        from_node = branch.from_node.item()
        to_node = branch.to_node.item()
        for field in dataclasses.fields(self):
            graph = getattr(self, field.name)
            if graph.active_only:
                graph.add_branch(from_ext_node_id=from_node, to_ext_node_id=to_node)

    def make_inactive(self, branch: BranchArray) -> None:
        """Remove a branch from all active_only graphs"""

        from_node = branch.from_node.item()
        to_node = branch.to_node.item()
        for field in dataclasses.fields(self):
            graph = getattr(self, field.name)
            if graph.active_only:
                graph.delete_branch(from_ext_node_id=from_node, to_ext_node_id=to_node)

    @classmethod
    def from_arrays(cls, arrays: "Grid") -> "GraphContainer":
        """Build from arrays"""
        cls._validate_branches(arrays=arrays)

        new_container = cls.empty()
        for graph_field in new_container.graph_attributes:
            graph = getattr(new_container, graph_field.name)
            new_graph = graph.from_arrays(arrays, active_only=graph.active_only)
            setattr(new_container, graph_field.name, new_graph)

        return new_container

    @staticmethod
    def _validate_branches(arrays: "Grid") -> None:
        for array in arrays.branch_arrays:
            if any(~np.isin(array.from_node, arrays.node.id)):
                raise RecordDoesNotExist(f"Found invalid .from_node values in {array.__class__.__name__}")
            if any(~np.isin(array.to_node, arrays.node.id)):
                raise RecordDoesNotExist(f"Found invalid .to_node values in {array.__class__.__name__}")

    def _append(self, array: FancyArray) -> None:
        if isinstance(array, NodeArray):
            self.add_node_array(array)
        if isinstance(array, BranchArray):
            self.add_branch_array(array)
        if isinstance(array, Branch3Array):
            self.add_branch3_array(array)
