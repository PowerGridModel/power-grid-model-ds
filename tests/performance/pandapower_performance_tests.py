from tests.performance._helpers import do_performance_test


def perf_test_add_lines():
    setup_code = {
        "grid": "from power_grid_model_ds import Grid;"
        + "from power_grid_model_ds._core.model.arrays import NodeArray, LineArray;"
        + "grid = Grid.empty()",
        "grid_batch": "from power_grid_model_ds import Grid;"
        + "from power_grid_model_ds._core.model.arrays import NodeArray, LineArray;"
        + "grid = Grid.empty()",
        "pandapower": "import pandapower as pp;" + "net = pp.create_empty_network()",
    }

    code_to_test = {
        "grid": "for i in range({size}): node_1 = NodeArray.zeros(1);"
        + "    grid.append(node_1);"
        + "    node_2 = NodeArray.zeros(1);"
        + "    grid.append(node_2);"
        + "    line = LineArray.zeros(1);"
        + "    line.from_node = node_1.id;"
        + "    line.to_node = node_2.id;"
        + "    grid.append(line)",
        "grid_batch": "nodes = NodeArray.zeros({size});"
        + "grid.append(nodes);"
        + "lines = LineArray.zeros({size});"
        + "lines.from_node = nodes.id;"
        + "lines.to_node = nodes.id;"
        + "grid.append(lines);",
        "pandapower": "for i in range({size}): b1 = pp.create_bus(net, vn_kv=20., name=f'Bus 1');"
        + "    b2 = pp.create_bus(net, vn_kv=20., name=f'Bus 2');"
        + '    pp.create_line(net, from_bus=b1, to_bus=b2, length_km=0.1, name="Line",std_type="NAYY 4x50 SE")',
    }

    do_performance_test(code_to_test, [10, 200], 10, setup_code)


if __name__ == "__main__":
    perf_test_add_lines()
