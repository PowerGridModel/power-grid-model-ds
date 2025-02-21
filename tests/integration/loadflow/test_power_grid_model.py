# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

import numpy as np
import pytest
from numpy.typing import NDArray
from power_grid_model import LoadGenType, TapChangingStrategy, initialize_array
from power_grid_model.enum import BranchSide, WindingType

from power_grid_model_ds._core.data_source.generator.grid_generators import RadialGridGenerator
from power_grid_model_ds._core.load_flow import PowerGridModelInterface
from power_grid_model_ds._core.model.arrays import (
    LineArray,
    LinkArray,
    NodeArray,
    SourceArray,
    SymLoadArray,
    ThreeWindingTransformerArray,
    TransformerArray,
)
from power_grid_model_ds._core.model.arrays.pgm_arrays import TransformerTapRegulatorArray
from power_grid_model_ds._core.model.grids.base import Grid
from tests.unit.model.grids.test_custom_grid import CustomGrid

# pylint: disable=missing-function-docstring,missing-class-docstring


class ExtendedNodeArray(NodeArray):
    """Extends the node array with an output value"""

    _defaults = {"u": 0}

    u: NDArray[np.float64]


class ExtendedLineArray(LineArray):
    """Extends the line array with an output value"""

    _defaults = {"i_from": 0}

    i_from: NDArray[np.float64]


def test_load_flow_on_random():
    """Tests the load flow on a randomly configured grid"""
    grid_generator = RadialGridGenerator(grid_class=Grid, nr_nodes=5, nr_sources=1, nr_nops=0)
    grid = grid_generator.run(seed=0)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # voltage should be in neighbourhood of 10500
    assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
    assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)
    # all lines have a current
    assert all(output["line"]["i_from"] > 0)


def test_load_flow(grid):
    """Tests the load flow on a test grid with 2 nodes"""
    nodes = NodeArray.zeros(2)
    nodes.id = [0, 1]
    nodes.u_rated = [10_500] * 2

    lines = LineArray.zeros(1)
    lines.id = [2]
    lines.from_node = [0]
    lines.to_node = [1]
    lines.from_status = [1]
    lines.to_status = [1]
    lines.r1 = [0.1]
    lines.x1 = [0.01]

    sources = SourceArray.zeros(1)
    sources.id = [3]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    loads = SymLoadArray.zeros(1)
    loads.id = [4]
    loads.node = [1]
    loads.status = [1]
    loads.type = [LoadGenType.const_power]
    loads.p_specified = [250_000]
    loads.q_specified = [50_000]

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # voltage should be in neighbourhood of 10500
    assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
    assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)
    # all lines have a current
    assert all(output["line"]["i_from"] > 0)


def test_load_flow_with_transformer(grid):
    """Tests the load flow on a test grid with 3 nodes and a trafo"""
    nodes = NodeArray.zeros(3)
    nodes.id = [0, 1, 2]
    nodes.u_rated = [10_500] * 2 + [3_000]

    lines = LineArray.zeros(1)
    lines.id = 3
    lines.from_node = 0
    lines.to_node = 1
    lines.from_status = 1
    lines.to_status = 1
    lines.r1 = 0.1
    lines.x1 = 0.01

    sources = SourceArray.zeros(1)
    sources.id = 4
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(2)
    loads.id = [5, 6]
    loads.node = [1, 2]
    loads.status = [1, 1]
    loads.p_specified = [25_000] * 2
    loads.q_specified = [5_000] * 2

    transformers = TransformerArray(
        id=[7],
        from_node=[1],
        to_node=[2],
        from_status=[1],
        to_status=[1],
        u1=[10_500],
        u2=[3_000],
        sn=[30e6],
        clock=[12],
        tap_size=[2.5e3],
        uk=[0.203],
        pk=[100e3],
        i0=[0.0],
        p0=[0.0],
        winding_from=[WindingType.wye.value],
        winding_to=[WindingType.wye.value],
        tap_side=[BranchSide.from_side.value],
        tap_pos=[0],
        tap_min=[-11],
        tap_max=[9],
        tap_nom=[0],
    )

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    grid.append(transformers)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # voltage should be in neighbourhood of 10500
    assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
    assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)
    assert output["node"]["u"][2] == pytest.approx(3_000, 0.1)

    # all lines have a current
    assert all(output["line"]["i_from"] > 0)


# pylint: disable=too-many-statements
# pylint: disable=duplicate-code
def test_load_flow_with_three_winding_transformer(grid):
    """Tests the load flow on a test grid with 3 nodes and a three winding trafo"""
    nodes = NodeArray.zeros(3)
    nodes.id = [0, 1, 2]
    nodes.u_rated = [150_000, 20_000, 10_000]

    sources = SourceArray.zeros(1)
    sources.id = 4
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(2)
    loads.id = [5, 6]
    loads.node = [1, 2]
    loads.status = [1, 1]
    loads.p_specified = [25_000] * 2
    loads.q_specified = [5_000] * 2

    three_winding_transformer = ThreeWindingTransformerArray.empty(1)
    three_winding_transformer.id = [7]
    three_winding_transformer.node_1 = [0]
    three_winding_transformer.node_2 = [1]
    three_winding_transformer.node_3 = [2]
    three_winding_transformer.status_1 = [1]
    three_winding_transformer.status_2 = [1]
    three_winding_transformer.status_3 = [1]
    three_winding_transformer.u1 = [150_000]
    three_winding_transformer.u2 = [20_000]
    three_winding_transformer.u3 = [10_000]
    three_winding_transformer.sn_1 = [1e5]
    three_winding_transformer.sn_2 = [1e5]
    three_winding_transformer.sn_3 = [1e5]
    three_winding_transformer.uk_12 = [0.09]
    three_winding_transformer.uk_13 = [0.06]
    three_winding_transformer.uk_23 = [0.06]
    three_winding_transformer.pk_12 = [1e3]
    three_winding_transformer.pk_13 = [1e3]
    three_winding_transformer.pk_23 = [1e3]
    three_winding_transformer.i0 = [0]
    three_winding_transformer.p0 = [0]
    three_winding_transformer.winding_1 = [2]
    three_winding_transformer.winding_2 = [1]
    three_winding_transformer.winding_3 = [1]
    three_winding_transformer.clock_12 = [5]
    three_winding_transformer.clock_13 = [5]
    three_winding_transformer.tap_side = [0]
    three_winding_transformer.tap_pos = [0]
    three_winding_transformer.tap_min = [-10]
    three_winding_transformer.tap_max = [10]
    three_winding_transformer.tap_nom = [0]
    three_winding_transformer.tap_size = [1380]

    grid.append(nodes)
    grid.append(sources)
    grid.append(loads)
    grid.append(three_winding_transformer)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # voltage should be in neighbourhood of 10500
    assert output["node"]["u"][0] == pytest.approx(150_000, 0.1)
    assert output["node"]["u"][1] == pytest.approx(20_000, 0.1)
    assert output["node"]["u"][2] == pytest.approx(10_000, 0.1)

    # transformer has loading
    assert all(output["three_winding_transformer"]["loading"] > 0)


def test_load_flow_with_link(grid):
    """Tests the load flow on a test grid with 2 nodes and a link"""
    nodes = NodeArray.zeros(2)
    nodes.id = [0, 1]
    nodes.u_rated = [10_500] * 2

    lines = LinkArray.zeros(1)
    lines.id = 2
    lines.from_node = 0
    lines.to_node = 1
    lines.from_status = 1
    lines.to_status = 1

    sources = SourceArray.zeros(1)
    sources.id = 3
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(1)
    loads.id = 4
    loads.node = 1
    loads.status = 1
    loads.type = [LoadGenType.const_power]
    loads.p_specified = [250_000]
    loads.q_specified = [50_000]

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # voltage should be in neighbourhood of 10500
    assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
    assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)

    # all lines have a current
    assert all(output["link"]["i_from"] > 0)


def test_automatic_tap_regulator(grid):
    """Test automatic tap regulator

    Network:
                        (tap_side)  (control side)
    source_1 --- node_2 --- transformer_5 --- node_3 --- line_6 --- node_4 --- load_7
                            |                    |
            transformer_tap_regulator_8 <--------/ (control voltage)

    """
    # source
    sources = SourceArray.zeros(1)
    sources.id = [1]
    sources.node = [2]
    sources.status = [1]
    sources.u_ref = [1.0]
    grid.append(sources)

    # node
    nodes = NodeArray.zeros(3)
    nodes.id = [2, 3, 4]
    nodes.u_rated = [1e4, 4e2, 4e2]
    grid.append(nodes)

    # transformer
    transformers = TransformerArray.zeros(1)
    transformers.id = [5]
    transformers.from_node = [2]
    transformers.to_node = [3]
    transformers.from_status = [1]
    transformers.to_status = [1]
    transformers.u1 = [1e4]
    transformers.u2 = [4e2]
    transformers.sn = [1e5]
    transformers.uk = [0.1]
    transformers.pk = [1e3]
    transformers.i0 = [1.0e-6]
    transformers.p0 = [0.1]
    transformers.winding_from = [2]
    transformers.winding_to = [1]
    transformers.clock = [5]
    transformers.tap_side = [0]
    transformers.tap_pos = [3]
    transformers.tap_min = [-11]
    transformers.tap_max = [9]
    transformers.tap_size = [100]
    grid.append(transformers)

    # line
    lines = LineArray.zeros(1)
    lines.id = [6]
    lines.from_node = [3]
    lines.to_node = [4]
    lines.from_status = [1]
    lines.to_status = [1]
    lines.r1 = [10.0]
    lines.x1 = [0.0]
    lines.c1 = [0.0]
    lines.tan1 = [0.0]
    grid.append(lines)

    # load
    sym_loads = SymLoadArray.zeros(1)
    sym_loads.id = [7]
    sym_loads.node = [4]
    sym_loads.status = [1]
    sym_loads.type = [LoadGenType.const_power]
    sym_loads.p_specified = [1e3]
    sym_loads.q_specified = [5e3]
    grid.append(sym_loads)

    # transformer tap regulator
    transformer_tap_regulators = TransformerTapRegulatorArray.zeros(1)
    transformer_tap_regulators.id = [8]
    transformer_tap_regulators.regulated_object = [5]
    transformer_tap_regulators.status = [1]
    transformer_tap_regulators.control_side = [BranchSide.to_side.value]
    transformer_tap_regulators.u_set = [400.0]
    transformer_tap_regulators.u_band = [20.0]
    transformer_tap_regulators.line_drop_compensation_r = [0.0]
    transformer_tap_regulators.line_drop_compensation_x = [0.0]
    grid.append(transformer_tap_regulators)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    output = core_interface.calculate_power_flow()

    # Without regulator the voltage at node_3 should be outside of band of transformer
    output = core_interface.calculate_power_flow(tap_changing_strategy=TapChangingStrategy.disabled)
    assert output["node"]["u"][1] < 390
    assert output["transformer_tap_regulator"]["tap_pos"][0] <= 0

    # Check that regulator is passed on and used to get node_3 within the band of transformer
    output = core_interface.calculate_power_flow(tap_changing_strategy=TapChangingStrategy.any_valid_tap)
    assert 390 < output["node"]["u"][1]
    assert output["node"]["u"][1] < 410
    assert output["transformer_tap_regulator"]["tap_pos"][0] > 0


def test_update_grid():
    """Tests the load flow on a randomly configured grid and update grid with results"""
    grid_generator = RadialGridGenerator(grid_class=Grid, nr_nodes=5, nr_sources=1, nr_nops=0)
    grid = grid_generator.run(seed=0)

    grid.node = ExtendedNodeArray(grid.node.data)
    grid.line = ExtendedLineArray(grid.line.data)

    core_interface = PowerGridModelInterface(grid=grid)
    core_interface.create_input_from_grid()
    core_interface.calculate_power_flow()
    core_interface.update_grid()

    # voltage should be in neighbourhood of 10500
    assert grid.node.u[0] == pytest.approx(10_500, 0.1)
    assert grid.node.u[1] == pytest.approx(10_500, 0.1)
    # all lines have a current
    assert all(grid.line.i_from > 0)


def test_update_model():
    """Test whether a pgm model can be updated and returns different results"""
    grid_generator = RadialGridGenerator(grid_class=Grid, nr_nodes=5, nr_sources=1, nr_nops=0)
    grid = grid_generator.run(seed=0)

    core_interface = PowerGridModelInterface(grid=grid)
    output_1 = core_interface.calculate_power_flow()

    update_sym_load = initialize_array("update", "sym_load", 2)
    update_sym_load["id"] = [12, 14]  # same ID
    update_sym_load["p_specified"] = [30e6, 15e6]  # change active power

    update_line = initialize_array("update", "line", 1)
    update_line["id"] = [18]  # change line ID 3
    update_line["from_status"] = [0]  # switch off at from side
    # leave to-side swichint status the same, no need to specify

    update_data = {"sym_load": update_sym_load, "line": update_line}

    core_interface.update_model(update_data)
    output_2 = core_interface.calculate_power_flow()
    # all results should be different
    assert not any(np.isclose(output_1["line"]["i_from"], output_2["line"]["i_from"]))
    assert not any(np.isclose(output_1["node"]["u"], output_2["node"]["u"]))


def test_batch_run():
    """Test whether a pgm model can be used in batch mode"""
    grid_generator = RadialGridGenerator(grid_class=Grid, nr_nodes=5, nr_sources=1, nr_nops=0)
    grid = grid_generator.run(seed=0)

    core_interface = PowerGridModelInterface(grid=grid)

    update_sym_load = initialize_array("update", "sym_load", (10, len(grid.sym_load)))
    update_sym_load["id"] = [grid.sym_load.id.tolist()]
    update_sym_load["p_specified"] = [grid.sym_load.p_specified.tolist()] * np.linspace(0, 1, 10).reshape(-1, 1)
    update_sym_load["q_specified"] = [grid.sym_load.q_specified.tolist()] * np.linspace(0, 1, 10).reshape(-1, 1)
    update_data = {
        "sym_load": update_sym_load,
    }
    output = core_interface.calculate_power_flow(update_data=update_data)

    # Results have been calculated for all 10 scenarios
    assert 10 == len(output["line"])


class CustomNodeArrayDefault(NodeArray):
    extra_field: NDArray[np.int64]

    _defaults = {"extra_field": 0}


@dataclass
class CustomGridDefault(Grid):
    node: CustomNodeArrayDefault


class TestCreateGridFromInputData:
    def test_create_grid_from_input_data(self, input_data_pgm):
        core_interface = PowerGridModelInterface(input_data=input_data_pgm)
        output = core_interface.create_grid_from_input_data()

        assert isinstance(output, Grid)
        assert isinstance(output.node, NodeArray)
        assert np.array_equal(
            output.node.data,
            np.array(
                [
                    (1, 10500.0, 0, -2147483648, -2147483648),
                    (2, 10500.0, 0, -2147483648, -2147483648),
                    (7, 10500.0, 0, -2147483648, -2147483648),
                ],
                dtype=[
                    ("id", "<i4"),
                    ("u_rated", "<f8"),
                    ("node_type", "i1"),
                    ("feeder_branch_id", "<i4"),
                    ("feeder_node_id", "<i4"),
                ],
            ),
        )

        assert isinstance(output.line, LineArray)
        assert np.array_equal(
            output.line.data,
            np.array(
                [
                    (
                        9,
                        7,
                        2,
                        1,
                        1,
                        -2147483648,
                        -2147483648,
                        False,
                        0.00396133,
                        4.53865336e-05,
                        0.0,
                        0.0,
                        303.91942029,
                    ),
                    (
                        10,
                        7,
                        1,
                        1,
                        1,
                        -2147483648,
                        -2147483648,
                        False,
                        0.32598809,
                        1.34716591e-02,
                        0.0,
                        0.0,
                        210.06857453,
                    ),
                ],
                dtype=[
                    ("id", "<i4"),
                    ("from_node", "<i4"),
                    ("to_node", "<i4"),
                    ("from_status", "i1"),
                    ("to_status", "i1"),
                    ("feeder_branch_id", "<i4"),
                    ("feeder_node_id", "<i4"),
                    ("is_feeder", "?"),
                    ("r1", "<f8"),
                    ("x1", "<f8"),
                    ("c1", "<f8"),
                    ("tan1", "<f8"),
                    ("i_n", "<f8"),
                ],
            ),
        )

        assert isinstance(output.sym_load, SymLoadArray)
        assert np.array_equal(
            output.sym_load.data,
            np.array(
                [(5, 1, 1, 0, -287484.0, 40640.0), (6, 2, 1, 0, 26558.0, 28148.0)],
                dtype=[
                    ("id", "<i4"),
                    ("node", "<i4"),
                    ("status", "i1"),
                    ("type", "i1"),
                    ("p_specified", "<f8"),
                    ("q_specified", "<f8"),
                ],
            ),
        )

        assert isinstance(output.source, SourceArray)
        assert np.array_equal(
            output.source.data,
            np.array([(8, 7, 1, 1.0)], dtype=[("id", "<i4"), ("node", "<i4"), ("status", "i1"), ("u_ref", "<f8")]),
        )

    def test_create_extended_grid_with_default_from_input_data(self, input_data_pgm):
        grid = CustomGridDefault.empty()

        core_interface = PowerGridModelInterface(grid=grid, input_data=input_data_pgm)

        output = core_interface.create_grid_from_input_data()

        assert isinstance(grid, CustomGridDefault)
        assert isinstance(grid.node, CustomNodeArrayDefault)
        assert np.array_equal(
            output.node.data,
            np.array(
                [
                    (1, 10500.0, 0, -2147483648, -2147483648, 0),
                    (2, 10500.0, 0, -2147483648, -2147483648, 0),
                    (7, 10500.0, 0, -2147483648, -2147483648, 0),
                ],
                dtype=[
                    ("id", "<i4"),
                    ("u_rated", "<f8"),
                    ("node_type", "i1"),
                    ("feeder_branch_id", "<i4"),
                    ("feeder_node_id", "<i4"),
                    ("extra_field", "<i8"),
                ],
            ),
        )

    def test_create_extended_grid_without_default_from_input_data(self, input_data_pgm):
        grid = CustomGrid.empty()

        core_interface = PowerGridModelInterface(grid=grid, input_data=input_data_pgm)

        with pytest.raises(ValueError, match="Missing required columns: {'extra_field'}"):
            core_interface.create_grid_from_input_data()
