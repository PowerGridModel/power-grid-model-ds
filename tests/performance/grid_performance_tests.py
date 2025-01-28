# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from tests.performance._helpers import do_performance_test

# pylint: disable=missing-function-docstring


def test_get_downstream_nodes_performance():
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
    test_get_downstream_nodes_performance()
