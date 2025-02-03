# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from tests.performance._helpers import do_graph_test

# pylint: disable=missing-function-docstring

GRAPH_SIZES = [100, 500, 1000, 5000]


def perftest_initialize():
    do_graph_test("pass", [10, 100], 100)


def perftest_get_components():
    code_to_test = (
        "from power_grid_model_ds._core.model.enums.nodes import NodeType;"
        + "feeder_node_ids=grid.node.filter(node_type=NodeType.SUBSTATION_NODE).id;"
        + "grid.graphs.active_graph.get_components(feeder_node_ids)"
    )
    do_graph_test(code_to_test, GRAPH_SIZES, 100)


def perftest_set_feeder_ids():
    code_to_test = "grid.set_feeder_ids()"
    do_graph_test(code_to_test, GRAPH_SIZES, 100)


def perftest_delete_node():
    code_to_test = "grid.delete_node(grid.node[0]);"
    do_graph_test(code_to_test, GRAPH_SIZES, 100)


def perftest_from_arrays():
    code_to_test = "grid.graphs.complete_graph.__class__.from_arrays(grid);"
    do_graph_test(code_to_test, GRAPH_SIZES, 100)


def perftest_add_node():
    code_to_test = (
        "from power_grid_model_ds._core.model.arrays import NodeArray;"
        + "new_node = NodeArray.zeros(1);"
        + "grid.add_node(node=new_node)"
    )
    do_graph_test(code_to_test, GRAPH_SIZES, 100)


if __name__ == "__main__":
    perftest_initialize()
    perftest_set_feeder_ids()
    perftest_get_components()
    perftest_delete_node()
    perftest_add_node()
    perftest_from_arrays()
