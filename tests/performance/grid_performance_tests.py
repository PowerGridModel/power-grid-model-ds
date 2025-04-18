# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from tests.performance._helpers import do_performance_test

# pylint: disable=missing-function-docstring


def perf_test_add_nodes():
    setup_code = {
        "grid": "from power_grid_model_ds import Grid;"
        + "from power_grid_model_ds._core.model.arrays import NodeArray;"
        + "grid = Grid.empty();"
        + "nodes = NodeArray.zeros({size});"
    }

    code_to_test = ["grid.append(nodes);"]

    do_performance_test(code_to_test, [10, 200, 1000], 100, setup_code)


def perf_test_add_lines():
    setup_code = {
        "grid": "from power_grid_model_ds import Grid;"
        + "from power_grid_model_ds._core.model.arrays import NodeArray, LineArray;"
        + "grid = Grid.empty();"
        + "nodes = NodeArray.zeros({size});"
        + "grid.append(nodes);"
        + "lines = LineArray.zeros({size});"
        + "lines.from_node = nodes.id;"
        + "lines.to_node = nodes.id;"
    }

    code_to_test = ["grid.append(lines);"]

    do_performance_test(code_to_test, [10, 200, 1000], 100, setup_code)


def perf_test_get_downstream_nodes_performance():
    setup_code = {
        "grid": "import numpy as np;"
        + "from power_grid_model_ds.enums import NodeType;"
        + "from power_grid_model_ds import Grid;"
        + "from power_grid_model_ds.generators import RadialGridGenerator;"
        + "from power_grid_model_ds.graph_models import RustworkxGraphModel;"
        + "grid=RadialGridGenerator(nr_nodes={size}, grid_class=Grid, graph_model=RustworkxGraphModel).run();"
        + "non_substation_node = grid.node.filter(node_type=NodeType.UNSPECIFIED).id;"
        + "node_id = np.random.choice(non_substation_node)"
    }

    code_to_test = [
        "grid.get_downstream_nodes(node_id)",
    ]

    do_performance_test(code_to_test, [10, 1000, 5000], 100, setup_code)


if __name__ == "__main__":
    perf_test_get_downstream_nodes_performance()
    perf_test_add_nodes()
    perf_test_add_lines()
