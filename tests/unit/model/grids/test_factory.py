# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for grid_extension_factory"""

import dataclasses
from dataclasses import field

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays import NodeArray
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.model.grids.factory import grid_extension_factory


class MonitoringArray(FancyArray):
    id: NDArray[np.int64]
    measurement: NDArray[np.float64]


class CustomNodeArray(NodeArray):
    pass


class TrackingGraphModel(RustworkxGraphModel):
    created_active_flags: list[bool] = []

    def __init__(self, active_only: bool = False) -> None:
        super().__init__(active_only=active_only)
        type(self).created_active_flags.append(active_only)


def test_grid_extension_factory_creates_dataclass() -> None:
    grid_cls, grid_instance = grid_extension_factory()

    assert grid_cls.__name__ == "DynamicExtendedGrid"
    assert dataclasses.is_dataclass(grid_cls)
    assert issubclass(grid_cls, Grid)
    assert isinstance(grid_instance, grid_cls)


def test_grid_extension_factory_registers_extra_arrays() -> None:
    grid_cls, grid_instance = grid_extension_factory(
        name="MonitoringGrid",
        user_arrays={"monitoring": MonitoringArray},
    )

    assert "monitoring" in grid_cls.__annotations__
    assert grid_cls.__annotations__["monitoring"] is MonitoringArray
    assert isinstance(grid_instance.monitoring, MonitoringArray)
    assert grid_instance.monitoring.size == 0


def test_grid_extension_factory_overrides_existing_array() -> None:
    grid_cls, grid_instance = grid_extension_factory(user_arrays={"node": CustomNodeArray})

    node_field = next(field for field in dataclasses.fields(grid_cls) if field.name == "node")
    assert node_field.type is CustomNodeArray
    assert isinstance(grid_instance.node, CustomNodeArray)


def test_grid_extension_factory_adds_value_fields() -> None:
    grid_cls, grid_instance = grid_extension_factory(
        user_fields={
            "owner": (str, "DSO"),
            "tags": (list[str], field(default_factory=list)),
        }
    )

    assert grid_cls.__annotations__["owner"] is str
    assert grid_instance.owner == "DSO"
    assert isinstance(grid_instance.tags, list)
    assert grid_instance.tags == []


def test_grid_extension_factory_uses_custom_graph_model() -> None:
    TrackingGraphModel.created_active_flags = []

    _, grid_instance = grid_extension_factory(graph_model=TrackingGraphModel)

    assert isinstance(grid_instance.graphs.active_graph, TrackingGraphModel)
    assert isinstance(grid_instance.graphs.complete_graph, TrackingGraphModel)
    assert TrackingGraphModel.created_active_flags == [True, False]
    assert grid_instance.graphs.active_graph.active_only is True
    assert grid_instance.graphs.complete_graph.active_only is False
