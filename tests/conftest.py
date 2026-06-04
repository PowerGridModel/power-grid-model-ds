# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper np.arrays used by various tests."""

import pytest
from power_grid_model import AttributeType, ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import FancyTestArray
from tests.fixtures.grids import build_basic_grid, build_basic_grid_with_three_winding, build_topologically_full_grid

# pylint: disable=missing-function-docstring

IMPLEMENTED_GRAPH_MODELS: dict[str, type[BaseGraphModel]] = {
    "rustworkx": RustworkxGraphModel,
}


def get_installed_graph_models() -> dict[str, type[BaseGraphModel]]:
    models: dict[str, type[BaseGraphModel]] = {
        model_name: graph_model
        for model_name, graph_model in IMPLEMENTED_GRAPH_MODELS.items()
        if graph_model is not None
    }
    if not models:
        raise ImportError("No graph models are installed")
    return models


@pytest.fixture
def grid() -> Grid:
    """A grid fixture that will be parametrized"""
    return Grid.empty()


@pytest.fixture
def graph() -> RustworkxGraphModel:
    """A graph fixture that will be parametrized"""
    return RustworkxGraphModel()


@pytest.fixture
def fancy_test_array():
    return FancyTestArray(
        id=[1, 2, 3],
        test_int=[3, 0, 4],
        test_float=[4.0, 4.0, 1.0],
        test_str=["a", "c", "d"],
        test_bool=[True, False, True],
    )


@pytest.fixture
def basic_grid(grid: Grid):
    return build_basic_grid(grid)


@pytest.fixture
def grid_with_3wt(grid: Grid):
    return build_basic_grid_with_three_winding(grid)


@pytest.fixture
def topologically_full_grid(grid: Grid):
    return build_topologically_full_grid(grid)


@pytest.fixture
def input_data_pgm():
    node = initialize_array(DatasetType.input, ComponentType.node, 3)
    node[AttributeType.id] = [1, 2, 7]
    node[AttributeType.u_rated] = [10500.0, 10500.0, 10500.0]

    line = initialize_array(DatasetType.input, ComponentType.line, 2)
    line[AttributeType.id] = [9, 10]
    line[AttributeType.from_node] = [7, 7]
    line[AttributeType.to_node] = [2, 1]
    line[AttributeType.from_status] = [1, 1]
    line[AttributeType.to_status] = [1, 1]
    line[AttributeType.r1] = [0.00396133, 0.32598809]
    line[AttributeType.x1] = [4.53865336e-05, 1.34716591e-02]
    line[AttributeType.c1] = [0.0, 0.0]
    line[AttributeType.tan1] = [0.0, 0.0]
    line[AttributeType.i_n] = [303.91942029, 210.06857453]

    link = initialize_array(DatasetType.input, ComponentType.link, 0)
    transformer = initialize_array(DatasetType.input, ComponentType.transformer, 0)
    three_winding_transformer = initialize_array(DatasetType.input, ComponentType.three_winding_transformer, 0)

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 2)
    sym_load[AttributeType.id] = [5, 6]
    sym_load[AttributeType.node] = [1, 2]
    sym_load[AttributeType.status] = [1, 1]
    sym_load[AttributeType.type] = [0, 0]
    sym_load[AttributeType.p_specified] = [-287484.0, 26558.0]
    sym_load[AttributeType.q_specified] = [40640.0, 28148.0]

    sym_gen = initialize_array(DatasetType.input, ComponentType.sym_gen, 0)

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source[AttributeType.id] = [8]
    source[AttributeType.node] = [7]
    source[AttributeType.status] = [1]
    source[AttributeType.u_ref] = [1.0]

    transformer_tap_regulator = initialize_array(DatasetType.input, ComponentType.transformer_tap_regulator, 0)
    sym_power_sensor = initialize_array(DatasetType.input, ComponentType.sym_power_sensor, 0)
    sym_voltage_sensor = initialize_array(DatasetType.input, ComponentType.sym_voltage_sensor, 0)
    asym_voltage_sensor = initialize_array(DatasetType.input, ComponentType.asym_voltage_sensor, 0)

    return {
        ComponentType.node: node,
        ComponentType.line: line,
        ComponentType.link: link,
        ComponentType.transformer: transformer,
        ComponentType.three_winding_transformer: three_winding_transformer,
        ComponentType.sym_load: sym_load,
        ComponentType.sym_gen: sym_gen,
        ComponentType.source: source,
        ComponentType.transformer_tap_regulator: transformer_tap_regulator,
        ComponentType.sym_power_sensor: sym_power_sensor,
        ComponentType.sym_voltage_sensor: sym_voltage_sensor,
        ComponentType.asym_voltage_sensor: asym_voltage_sensor,
    }
