# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper np.arrays used by various tests."""

import pytest
from power_grid_model import initialize_array

from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import FancyTestArray
from tests.fixtures.grids import build_basic_grid, build_basic_grid_with_three_winding

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


def pytest_generate_tests(
    metafunc: pytest.Metafunc,
) -> None:
    """Parametrize the graph fixture"""
    installed_graph_models = get_installed_graph_models()
    if "grid" in metafunc.fixturenames:
        grids = [Grid.empty(graph_model=graph) for graph in installed_graph_models.values()]
        metafunc.parametrize(
            argnames=["grid"],
            argvalues=[[grid] for grid in grids],
            ids=list(installed_graph_models.keys()),
        )

    if "graph" in metafunc.fixturenames:
        metafunc.parametrize(
            argnames=["graph"],
            argvalues=[[graph()] for graph in installed_graph_models.values()],
            ids=list(installed_graph_models.keys()),
        )


@pytest.fixture
def fancy_test_array():
    yield FancyTestArray(
        id=[1, 2, 3],
        test_int=[3, 0, 4],
        test_float=[4.0, 4.0, 1.0],
        test_str=["a", "c", "d"],
        test_bool=[True, False, True],
    )


@pytest.fixture
def basic_grid(grid: Grid):
    yield build_basic_grid(grid)


@pytest.fixture
def grid_with_3wt(grid: Grid):
    yield build_basic_grid_with_three_winding(grid)


@pytest.fixture
def input_data_pgm():
    node = initialize_array("input", "node", 3)
    node["id"] = [1, 2, 7]
    node["u_rated"] = [10500.0, 10500.0, 10500.0]

    line = initialize_array("input", "line", 2)
    line["id"] = [9, 10]
    line["from_node"] = [7, 7]
    line["to_node"] = [2, 1]
    line["from_status"] = [1, 1]
    line["to_status"] = [1, 1]
    line["r1"] = [0.00396133, 0.32598809]
    line["x1"] = [4.53865336e-05, 1.34716591e-02]
    line["c1"] = [0.0, 0.0]
    line["tan1"] = [0.0, 0.0]
    line["i_n"] = [303.91942029, 210.06857453]

    link = initialize_array("input", "link", 0)
    transformer = initialize_array("input", "transformer", 0)
    three_winding_transformer = initialize_array("input", "three_winding_transformer", 0)

    sym_load = initialize_array("input", "sym_load", 2)
    sym_load["id"] = [5, 6]
    sym_load["node"] = [1, 2]
    sym_load["status"] = [1, 1]
    sym_load["type"] = [0, 0]
    sym_load["p_specified"] = [-287484.0, 26558.0]
    sym_load["q_specified"] = [40640.0, 28148.0]

    sym_gen = initialize_array("input", "sym_gen", 0)

    source = initialize_array("input", "source", 1)
    source["id"] = [8]
    source["node"] = [7]
    source["status"] = [1]
    source["u_ref"] = [1.0]

    transformer_tap_regulator = initialize_array("input", "transformer_tap_regulator", 0)
    sym_power_sensor = initialize_array("input", "sym_power_sensor", 0)
    sym_voltage_sensor = initialize_array("input", "sym_voltage_sensor", 0)
    asym_voltage_sensor = initialize_array("input", "asym_voltage_sensor", 0)

    return {
        "node": node,
        "line": line,
        "link": link,
        "transformer": transformer,
        "three_winding_transformer": three_winding_transformer,
        "sym_load": sym_load,
        "sym_gen": sym_gen,
        "source": source,
        "transformer_tap_regulator": transformer_tap_regulator,
        "sym_power_sensor": sym_power_sensor,
        "sym_voltage_sensor": sym_voltage_sensor,
        "asym_voltage_sensor": asym_voltage_sensor,
    }
