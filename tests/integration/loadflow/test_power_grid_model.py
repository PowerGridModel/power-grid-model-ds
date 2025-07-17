# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import numpy as np
import pytest
from power_grid_model import TapChangingStrategy, initialize_array

from power_grid_model_ds._core.data_source.generator.grid_generators import RadialGridGenerator
from power_grid_model_ds._core.load_flow import PowerGridModelInterface
from power_grid_model_ds._core.model.arrays import (
    LineArray,
    NodeArray,
    SourceArray,
    SymLoadArray,
)
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import ExtendedLineArray, ExtendedNodeArray
from tests.fixtures.grid_classes import ExtendedGrid
from tests.unit.model.grids.test_custom_grid import CustomGrid

# pylint: disable=missing-function-docstring,missing-class-docstring


class TestCalculatePowerFlow:
    def test_load_flow_on_random_grid(self):
        """Tests the power flow on a randomly configured grid"""
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

    def test_simple_grid(self, simple_loadflow_grid: Grid):
        """Tests the power flow on a test grid with 2 nodes"""
        core_interface = PowerGridModelInterface(grid=simple_loadflow_grid)
        core_interface.create_input_from_grid()
        output = core_interface.calculate_power_flow()

        # voltage should be in neighbourhood of 10500
        assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
        assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)
        # all lines have a current
        assert all(output["line"]["i_from"] > 0)

    def test_grid_with_transformer(self, loadflow_grid_with_transformer: Grid):
        """Tests the power flow on a test grid with 3 nodes and a trafo"""
        core_interface = PowerGridModelInterface(grid=loadflow_grid_with_transformer)
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
    def test_grid_with_three_winding_transformer(self, grid_with_three_winding_transformer: Grid):
        """Tests the power flow on a test grid with 3 nodes and a three winding trafo"""

        core_interface = PowerGridModelInterface(grid=grid_with_three_winding_transformer)
        core_interface.create_input_from_grid()
        output = core_interface.calculate_power_flow()

        # voltage should be in neighbourhood of 10500
        assert output["node"]["u"][0] == pytest.approx(150_000, 0.1)
        assert output["node"]["u"][1] == pytest.approx(20_000, 0.1)
        assert output["node"]["u"][2] == pytest.approx(10_000, 0.1)

        # transformer has loading
        assert all(output["three_winding_transformer"]["loading"] > 0)

    def test_grid_with_link(self, grid_with_link: Grid):
        """Tests the power flow on a test grid with 2 nodes and a link"""
        core_interface = PowerGridModelInterface(grid=grid_with_link)
        core_interface.create_input_from_grid()
        output = core_interface.calculate_power_flow()

        # voltage should be in neighbourhood of 10500
        assert output["node"]["u"][0] == pytest.approx(10_500, 0.1)
        assert output["node"]["u"][1] == pytest.approx(10_500, 0.1)

        # all lines have a current
        assert all(output["link"]["i_from"] > 0)

    def test_grid_with_automatic_tap_regulator(self, grid_with_tap_regulator: Grid):
        core_interface = PowerGridModelInterface(grid=grid_with_tap_regulator)
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


class PowerGridModelInterfaceMethods:
    def test_update_grid(self):
        """Tests the power flow on a randomly configured grid and update grid with results"""
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

    def test_update_model(self):
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

    def test_batch_run(self):
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

    def test_setup_model(self):
        """Test whether a pgm model can be setup with a custom grid"""
        grid_generator = RadialGridGenerator(grid_class=CustomGrid, nr_nodes=5, nr_sources=1, nr_nops=0)
        grid = grid_generator.run(seed=0)

        core_interface = PowerGridModelInterface(grid=grid)
        assert core_interface.model is None
        assert core_interface._input_data is None
        core_interface.setup_model()
        assert core_interface.model
        assert core_interface._input_data


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
        grid = ExtendedGrid.empty()

        core_interface = PowerGridModelInterface(grid=grid, input_data=input_data_pgm)

        output = core_interface.create_grid_from_input_data()

        assert isinstance(grid, ExtendedGrid)
        assert isinstance(grid.node, ExtendedNodeArray)
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
                    ("u", "<f8"),
                ],
            ),
        )

    def test_create_extended_grid_without_default_from_input_data(self, input_data_pgm):
        grid = CustomGrid.empty()

        core_interface = PowerGridModelInterface(grid=grid, input_data=input_data_pgm)

        with pytest.raises(ValueError, match="Missing required columns: {'extra_field'}"):
            core_interface.create_grid_from_input_data()
