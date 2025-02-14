# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper np.arrays used by various tests."""

import numpy as np
import pytest

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
def basic_grid(grid):
    yield build_basic_grid(grid)


@pytest.fixture
def grid_with_3wt(grid):
    yield build_basic_grid_with_three_winding(grid)


@pytest.fixture
def input_data_pgm():
    return {
        "node": np.array(
            [(1, 10500.0), (2, 10500.0), (7, 10500.0)],
            dtype={
                "names": ["id", "u_rated"],
                "formats": ["<i4", "<f8"],
                "offsets": [0, 8],
                "itemsize": 16,
                "aligned": True,
            },
        ),
        "line": np.array(
            [
                (9, 7, 2, 1, 1, 0.00396133, 4.53865336e-05, 0.0, 0.0, np.nan, np.nan, np.nan, np.nan, 303.91942029),
                (10, 7, 1, 1, 1, 0.32598809, 1.34716591e-02, 0.0, 0.0, np.nan, np.nan, np.nan, np.nan, 210.06857453),
            ],
            dtype={
                "names": [
                    "id",
                    "from_node",
                    "to_node",
                    "from_status",
                    "to_status",
                    "r1",
                    "x1",
                    "c1",
                    "tan1",
                    "r0",
                    "x0",
                    "c0",
                    "tan0",
                    "i_n",
                ],
                "formats": [
                    "<i4",
                    "<i4",
                    "<i4",
                    "i1",
                    "i1",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                ],
                "offsets": [0, 4, 8, 12, 13, 16, 24, 32, 40, 48, 56, 64, 72, 80],
                "itemsize": 88,
                "aligned": True,
            },
        ),
        "link": np.array(
            [],
            dtype={
                "names": ["id", "from_node", "to_node", "from_status", "to_status"],
                "formats": ["<i4", "<i4", "<i4", "i1", "i1"],
                "offsets": [0, 4, 8, 12, 13],
                "itemsize": 16,
                "aligned": True,
            },
        ),
        "transformer": np.array(
            [],
            dtype={
                "names": [
                    "id",
                    "from_node",
                    "to_node",
                    "from_status",
                    "to_status",
                    "u1",
                    "u2",
                    "sn",
                    "uk",
                    "pk",
                    "i0",
                    "p0",
                    "winding_from",
                    "winding_to",
                    "clock",
                    "tap_side",
                    "tap_pos",
                    "tap_min",
                    "tap_max",
                    "tap_nom",
                    "tap_size",
                    "uk_min",
                    "uk_max",
                    "pk_min",
                    "pk_max",
                    "r_grounding_from",
                    "x_grounding_from",
                    "r_grounding_to",
                    "x_grounding_to",
                ],
                "formats": [
                    "<i4",
                    "<i4",
                    "<i4",
                    "i1",
                    "i1",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                ],
                "offsets": [
                    0,
                    4,
                    8,
                    12,
                    13,
                    16,
                    24,
                    32,
                    40,
                    48,
                    56,
                    64,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    88,
                    96,
                    104,
                    112,
                    120,
                    128,
                    136,
                    144,
                ],
                "itemsize": 152,
                "aligned": True,
            },
        ),
        "three_winding_transformer": np.array(
            [],
            dtype={
                "names": [
                    "id",
                    "node_1",
                    "node_2",
                    "node_3",
                    "status_1",
                    "status_2",
                    "status_3",
                    "u1",
                    "u2",
                    "u3",
                    "sn_1",
                    "sn_2",
                    "sn_3",
                    "uk_12",
                    "uk_13",
                    "uk_23",
                    "pk_12",
                    "pk_13",
                    "pk_23",
                    "i0",
                    "p0",
                    "winding_1",
                    "winding_2",
                    "winding_3",
                    "clock_12",
                    "clock_13",
                    "tap_side",
                    "tap_pos",
                    "tap_min",
                    "tap_max",
                    "tap_nom",
                    "tap_size",
                    "uk_12_min",
                    "uk_12_max",
                    "uk_13_min",
                    "uk_13_max",
                    "uk_23_min",
                    "uk_23_max",
                    "pk_12_min",
                    "pk_12_max",
                    "pk_13_min",
                    "pk_13_max",
                    "pk_23_min",
                    "pk_23_max",
                    "r_grounding_1",
                    "x_grounding_1",
                    "r_grounding_2",
                    "x_grounding_2",
                    "r_grounding_3",
                    "x_grounding_3",
                ],
                "formats": [
                    "<i4",
                    "<i4",
                    "<i4",
                    "<i4",
                    "i1",
                    "i1",
                    "i1",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "i1",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                    "<f8",
                ],
                "offsets": [
                    0,
                    4,
                    8,
                    12,
                    16,
                    17,
                    18,
                    24,
                    32,
                    40,
                    48,
                    56,
                    64,
                    72,
                    80,
                    88,
                    96,
                    104,
                    112,
                    120,
                    128,
                    136,
                    137,
                    138,
                    139,
                    140,
                    141,
                    142,
                    143,
                    144,
                    145,
                    152,
                    160,
                    168,
                    176,
                    184,
                    192,
                    200,
                    208,
                    216,
                    224,
                    232,
                    240,
                    248,
                    256,
                    264,
                    272,
                    280,
                    288,
                    296,
                ],
                "itemsize": 304,
                "aligned": True,
            },
        ),
        "sym_load": np.array(
            [(5, 1, 1, 0, -287484.0, 40640.0), (6, 2, 1, 0, 26558.0, 28148.0)],
            dtype={
                "names": ["id", "node", "status", "type", "p_specified", "q_specified"],
                "formats": ["<i4", "<i4", "i1", "i1", "<f8", "<f8"],
                "offsets": [0, 4, 8, 9, 16, 24],
                "itemsize": 32,
                "aligned": True,
            },
        ),
        "sym_gen": np.array(
            [],
            dtype={
                "names": ["id", "node", "status", "type", "p_specified", "q_specified"],
                "formats": ["<i4", "<i4", "i1", "i1", "<f8", "<f8"],
                "offsets": [0, 4, 8, 9, 16, 24],
                "itemsize": 32,
                "aligned": True,
            },
        ),
        "source": np.array(
            [(8, 7, 1, 1.0, np.nan, np.nan, np.nan, np.nan)],
            dtype={
                "names": ["id", "node", "status", "u_ref", "u_ref_angle", "sk", "rx_ratio", "z01_ratio"],
                "formats": ["<i4", "<i4", "i1", "<f8", "<f8", "<f8", "<f8", "<f8"],
                "offsets": [0, 4, 8, 16, 24, 32, 40, 48],
                "itemsize": 56,
                "aligned": True,
            },
        ),
        "transformer_tap_regulator": np.array(
            [],
            dtype={
                "names": [
                    "id",
                    "regulated_object",
                    "status",
                    "control_side",
                    "u_set",
                    "u_band",
                    "line_drop_compensation_r",
                    "line_drop_compensation_x",
                ],
                "formats": ["<i4", "<i4", "i1", "i1", "<f8", "<f8", "<f8", "<f8"],
                "offsets": [0, 4, 8, 9, 16, 24, 32, 40],
                "itemsize": 48,
                "aligned": True,
            },
        ),
        "sym_power_sensor": np.array(
            [],
            dtype={
                "names": [
                    "id",
                    "measured_object",
                    "measured_terminal_type",
                    "power_sigma",
                    "p_measured",
                    "q_measured",
                    "p_sigma",
                    "q_sigma",
                ],
                "formats": ["<i4", "<i4", "i1", "<f8", "<f8", "<f8", "<f8", "<f8"],
                "offsets": [0, 4, 8, 16, 24, 32, 40, 48],
                "itemsize": 56,
                "aligned": True,
            },
        ),
        "sym_voltage_sensor": np.array(
            [],
            dtype={
                "names": ["id", "measured_object", "u_sigma", "u_measured", "u_angle_measured"],
                "formats": ["<i4", "<i4", "<f8", "<f8", "<f8"],
                "offsets": [0, 4, 8, 16, 24],
                "itemsize": 32,
                "aligned": True,
            },
        ),
        "asym_voltage_sensor": np.array(
            [],
            dtype={
                "names": ["id", "measured_object", "u_sigma", "u_measured", "u_angle_measured"],
                "formats": ["<i4", "<i4", "<f8", ("<f8", (3,)), ("<f8", (3,))],
                "offsets": [0, 4, 8, 16, 40],
                "itemsize": 64,
                "aligned": True,
            },
        ),
    }
