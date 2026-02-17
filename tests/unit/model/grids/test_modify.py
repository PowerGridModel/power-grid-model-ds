# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import (
    AsymGenArray,
    AsymLoadArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    FaultArray,
    LineArray,
    LinkArray,
    NodeArray,
    ShuntArray,
    SourceArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
    VoltageRegulatorArray,
)
from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymCurrentSensorArray,
    AsymLineArray,
    GenericBranchArray,
    SymCurrentSensorArray,
    SymGenArray,
)
from power_grid_model_ds._core.model.constants import EMPTY_ID
from tests.fixtures.arrays import DefaultedCustomLineArray, DefaultedCustomNodeArray
from tests.fixtures.grid_classes import ExtendedGrid


def test_grid_add_node(basic_grid: Grid):
    grid = basic_grid

    new_node = NodeArray.zeros(1)
    grid.add_node(node=new_node)

    assert 7 == len(grid.node)
    assert EMPTY_ID not in grid.node.id
    assert grid.node[-1].id.item() in grid.graphs.complete_graph.external_ids
    assert EMPTY_ID not in grid.graphs.complete_graph.external_ids


def test_grid_delete_node(basic_grid: Grid):
    grid = basic_grid

    target_node = grid.node.get(101)
    grid.delete_node(node=target_node)

    assert 5 == len(grid.node)
    assert target_node.id not in grid.node.id


@pytest.mark.parametrize(
    "three_winding_node_id,expected_length_three_winding_transformers",
    [
        pytest.param(101, 0, id="Three winding transformer connected to node to delete"),
        pytest.param(102, 1, id="Three winding transformer not connected to node to delete"),
    ],
)
def test_grid_delete_node_with_three_winding_transformer(
    three_winding_node_id: int, expected_length_three_winding_transformers: int, basic_grid: Grid
):
    grid = basic_grid

    new_three_winding_transformer = ThreeWindingTransformerArray.empty(1)
    new_three_winding_transformer.id = 701
    new_three_winding_transformer.node_1 = three_winding_node_id
    new_three_winding_transformer.node_2 = 103
    new_three_winding_transformer.node_3 = 104
    grid.append(new_three_winding_transformer)

    target_node = grid.node.get(101)
    grid.delete_node(node=target_node)

    assert 5 == len(grid.node)
    assert expected_length_three_winding_transformers == len(grid.three_winding_transformer)
    assert target_node.id not in grid.node.id


def test_grid_delete_node_all(topologically_full_grid: Grid):
    grid = topologically_full_grid

    target_node = grid.node.get(1001)
    grid.delete_node(node=target_node)

    assert 1001 not in grid.node.id
    assert all(
        id in grid.node.id
        for id in [1002, 1003, 1004, 1005, 1006, 1007, 1008, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
    )

    assert 10001 not in grid.line.id
    assert 20001 in grid.line.id

    assert 10002 not in grid.link.id
    assert 20002 in grid.link.id

    assert 10003 not in grid.asym_line.id
    assert 20003 in grid.asym_line.id

    assert 10004 not in grid.generic_branch.id
    assert 20004 in grid.generic_branch.id

    assert 10005 not in grid.transformer.id
    assert 20005 in grid.transformer.id

    assert 10006 not in grid.three_winding_transformer.id
    assert 20006 in grid.three_winding_transformer.id

    assert 11001 not in grid.source.id
    assert 21001 in grid.source.id

    assert 11002 not in grid.shunt.id
    assert 21002 in grid.shunt.id

    assert 11003 not in grid.sym_load.id
    assert 21003 in grid.sym_load.id

    assert 11004 not in grid.sym_gen.id
    assert 21004 in grid.sym_gen.id

    assert 11005 not in grid.asym_load.id
    assert 21005 in grid.asym_load.id

    assert 11006 not in grid.asym_gen.id
    assert 21006 in grid.asym_gen.id

    assert 11007 not in grid.fault.id
    assert 21007 in grid.fault.id

    assert 12001 not in grid.sym_voltage_sensor.id
    assert 22001 in grid.sym_voltage_sensor.id

    assert 12002 not in grid.asym_voltage_sensor.id
    assert 22002 in grid.asym_voltage_sensor.id

    assert 12003 not in grid.sym_power_sensor.id
    assert all(
        id in grid.sym_power_sensor.id
        for id in [22003, 22004, 22005, 22006, 22007, 22008, 22009, 22010, 22011, 22012, 22013, 22014, 22015]
    )

    assert 12016 not in grid.asym_power_sensor.id
    assert all(
        id in grid.asym_power_sensor.id
        for id in [22016, 22017, 22018, 22019, 22020, 22021, 22022, 22023, 22024, 22025, 22026, 22027, 22028]
    )

    assert 12029 not in grid.sym_current_sensor.id
    assert all(id in grid.sym_current_sensor.id for id in [22029, 22030, 22031, 22032, 22033, 22034])

    assert 12035 not in grid.asym_current_sensor.id
    assert all(id in grid.asym_current_sensor.id for id in [22035, 22036, 22037, 22038, 22039, 22040])

    assert 13001 not in grid.voltage_regulator.id
    assert all(id in grid.voltage_regulator.id for id in [23001, 23002, 23003, 23004])

    assert 13005 not in grid.transformer_tap_regulator.id
    assert all(id in grid.transformer_tap_regulator.id for id in [23005, 23006])


@pytest.mark.parametrize(
    "branch_array_class",
    [LineArray, LinkArray, TransformerArray, GenericBranchArray, AsymLineArray],
)
def test_grid_delete_branch_all(branch_array_class):
    grid = Grid.empty()

    nodes = NodeArray.zeros(3)
    nodes.id = [10, 11, 12]
    grid.append(nodes)

    branch = branch_array_class.zeros(2)
    branch.id = [99, 101]
    branch.from_node = [10, 11]
    branch.to_node = [11, 12]
    grid.append(branch)

    sym_power_sensors = SymPowerSensorArray.zeros(2)
    sym_power_sensors.id = [200, 201]
    sym_power_sensors.measured_object = [99, 101]
    grid.append(sym_power_sensors)

    asym_power_sensors = AsymPowerSensorArray.zeros(2)
    asym_power_sensors.id = [300, 301]
    asym_power_sensors.measured_object = [99, 101]
    grid.append(asym_power_sensors)

    sym_current_sensors = SymCurrentSensorArray.zeros(2)
    sym_current_sensors.id = [400, 401]
    sym_current_sensors.measured_object = [99, 101]
    grid.append(sym_current_sensors)

    asym_current_sensors = AsymCurrentSensorArray.zeros(2)
    asym_current_sensors.id = [500, 501]
    asym_current_sensors.measured_object = [99, 101]
    grid.append(asym_current_sensors)

    transformer_regulators = TransformerTapRegulatorArray.zeros(2)
    transformer_regulators.id = [600, 601]
    transformer_regulators.regulated_object = [99, 101]
    grid.append(transformer_regulators)

    # Verify
    assert grid.graphs.complete_graph.has_branch(10, 11)
    assert grid.graphs.complete_graph.has_branch(11, 12)

    # Act
    branch_name = grid.find_array_field(branch_array_class).name
    target_branch = getattr(grid, branch_name).get(99)
    grid.delete_branch(branch=target_branch)

    # Assert
    assert 99 not in getattr(grid, branch_name).id
    assert 101 in getattr(grid, branch_name).id

    assert 200 not in grid.sym_power_sensor.id
    assert 201 in grid.sym_power_sensor.id

    assert 300 not in grid.asym_power_sensor.id
    assert 301 in grid.asym_power_sensor.id

    assert 400 not in grid.sym_current_sensor.id
    assert 401 in grid.sym_current_sensor.id

    assert 500 not in grid.asym_current_sensor.id
    assert 501 in grid.asym_current_sensor.id

    assert 600 not in grid.transformer_tap_regulator.id
    assert 601 in grid.transformer_tap_regulator.id

    assert not grid.graphs.complete_graph.has_branch(10, 11)
    assert grid.graphs.complete_graph.has_branch(11, 12)


def test_grid_delete_branch3_all():
    grid = Grid.empty()

    nodes = NodeArray.zeros(5)
    nodes.id = [10, 11, 12, 13, 14]
    grid.append(nodes)

    branch3 = ThreeWindingTransformerArray.zeros(2)
    branch3.id = [99, 101]
    branch3.node_1 = [10, 12]
    branch3.node_2 = [11, 13]
    branch3.node_3 = [12, 14]
    grid.append(branch3)

    sym_power_sensors = SymPowerSensorArray.zeros(2)
    sym_power_sensors.id = [200, 201]
    sym_power_sensors.measured_object = [99, 101]
    grid.append(sym_power_sensors)

    asym_power_sensors = AsymPowerSensorArray.zeros(2)
    asym_power_sensors.id = [300, 301]
    asym_power_sensors.measured_object = [99, 101]
    grid.append(asym_power_sensors)

    sym_current_sensors = SymCurrentSensorArray.zeros(2)
    sym_current_sensors.id = [400, 401]
    sym_current_sensors.measured_object = [99, 101]
    grid.append(sym_current_sensors)

    asym_current_sensors = AsymCurrentSensorArray.zeros(2)
    asym_current_sensors.id = [500, 501]
    asym_current_sensors.measured_object = [99, 101]
    grid.append(asym_current_sensors)

    transformer_regulators = TransformerTapRegulatorArray.zeros(2)
    transformer_regulators.id = [600, 601]
    transformer_regulators.regulated_object = [99, 101]
    grid.append(transformer_regulators)

    # Verify
    assert grid.graphs.complete_graph.has_branch(10, 11)
    assert grid.graphs.complete_graph.has_branch(11, 12)
    assert grid.graphs.complete_graph.has_branch(12, 10)
    assert grid.graphs.complete_graph.has_branch(12, 13)
    assert grid.graphs.complete_graph.has_branch(13, 14)
    assert grid.graphs.complete_graph.has_branch(14, 12)

    # Act
    grid.delete_branch3(branch=branch3.get(99))

    # Assert
    assert 99 not in grid.three_winding_transformer.id
    assert 101 in grid.three_winding_transformer.id

    assert 200 not in grid.sym_power_sensor.id
    assert 201 in grid.sym_power_sensor.id

    assert 300 not in grid.asym_power_sensor.id
    assert 301 in grid.asym_power_sensor.id

    assert 400 not in grid.sym_current_sensor.id
    assert 401 in grid.sym_current_sensor.id

    assert 500 not in grid.asym_current_sensor.id
    assert 501 in grid.asym_current_sensor.id

    assert 600 not in grid.transformer_tap_regulator.id
    assert 601 in grid.transformer_tap_regulator.id

    assert not grid.graphs.complete_graph.has_branch(10, 11)
    assert not grid.graphs.complete_graph.has_branch(11, 12)
    assert not grid.graphs.complete_graph.has_branch(12, 10)
    assert grid.graphs.complete_graph.has_branch(12, 13)
    assert grid.graphs.complete_graph.has_branch(13, 14)
    assert grid.graphs.complete_graph.has_branch(14, 12)


@pytest.mark.parametrize(
    "appliance_array_class",
    [SymLoadArray, AsymLoadArray, AsymGenArray, SourceArray, ShuntArray, SymGenArray],
)
def test_grid_delete_appliance_all(appliance_array_class):
    grid = Grid.empty()

    nodes = NodeArray.zeros(2)
    nodes.id = [99, 100]
    grid.append(nodes)

    appliance = appliance_array_class.zeros(2)
    appliance.id = [200, 201]
    appliance.node = [99, 100]
    grid.append(appliance)

    sym_power_sensors = SymPowerSensorArray.zeros(2)
    sym_power_sensors.id = [300, 301]
    sym_power_sensors.measured_object = [200, 201]
    grid.append(sym_power_sensors)

    asym_power_sensors = AsymPowerSensorArray.zeros(2)
    asym_power_sensors.id = [400, 401]
    asym_power_sensors.measured_object = [200, 201]
    grid.append(asym_power_sensors)

    if appliance_array_class in [SymGenArray, SymLoadArray, AsymLoadArray, AsymGenArray]:
        voltage_regulator_array = VoltageRegulatorArray.zeros(2)
        voltage_regulator_array.id = [500, 501]
        voltage_regulator_array.regulated_object = [200, 201]
        grid.append(voltage_regulator_array)

    # Act
    appliance_name = grid.find_array_field(appliance_array_class).name
    target_appliance = getattr(grid, appliance_name).get(200)
    grid.delete_appliance(target_appliance)

    # Assert
    assert 200 not in getattr(grid, appliance_name).id
    assert 201 in getattr(grid, appliance_name).id

    assert 300 not in grid.sym_power_sensor.id
    assert 301 in grid.sym_power_sensor.id

    assert 400 not in grid.asym_power_sensor.id
    assert 401 in grid.asym_power_sensor.id

    if appliance_array_class in [SymGenArray, SymLoadArray, AsymLoadArray, AsymGenArray]:
        assert 500 not in grid.voltage_regulator.id
        assert 501 in grid.voltage_regulator.id


# pylint: disable=no-member
def test_grid_add_line(basic_grid: Grid):
    grid = basic_grid

    line = LineArray.zeros(1)
    line.from_node = 102
    line.to_node = 105

    assert not grid.graphs.complete_graph.has_branch(102, 105)

    grid.add_branch(branch=line)

    assert 5 == len(grid.line)
    assert EMPTY_ID not in grid.line.id
    assert grid.graphs.complete_graph.has_branch(102, 105)


def test_grid_delete_line(basic_grid: Grid):
    grid = basic_grid

    line = grid.line.get(201)

    assert grid.graphs.complete_graph.has_branch(line.from_node.item(), line.to_node.item())

    grid.delete_branch(branch=line)

    assert 3 == len(grid.line)
    assert line.id not in grid.line.id

    assert not grid.graphs.complete_graph.has_branch(line.from_node.item(), line.to_node.item())


def test_grid_delete_inactive_line(basic_grid: Grid):
    grid = basic_grid

    inactive_mask = grid.line.from_status == 0
    target_line = grid.line[inactive_mask]

    assert grid.graphs.complete_graph.has_branch(target_line.from_node.item(), target_line.to_node.item())

    grid.delete_branch(branch=target_line)

    assert 3 == len(grid.line)
    assert target_line.id not in grid.line.id

    assert not grid.graphs.complete_graph.has_branch(target_line.from_node.item(), target_line.to_node.item())


def test_grid_delete_transformer_with_regulator(basic_grid: Grid):
    grid = basic_grid
    transformer_regulator = TransformerTapRegulatorArray.zeros(1)
    transformer_regulator.regulated_object = 301
    grid.append(transformer_regulator)

    assert 1 == len(grid.transformer_tap_regulator)

    transformer = grid.transformer.get(id=301)
    grid.delete_branch(branch=transformer)

    assert 0 == len(grid.transformer)
    assert transformer.id not in grid.transformer.id


def test_grid_add_link(basic_grid: Grid):
    grid = basic_grid

    new_link_array = LinkArray.zeros(1)
    new_link_array.from_node = 105
    new_link_array.to_node = 103

    assert 1 == len(grid.link)
    assert not grid.graphs.complete_graph.has_branch(105, 103)
    grid.add_branch(new_link_array)
    assert 2 == len(grid.link)
    assert EMPTY_ID not in grid.link.id
    assert grid.graphs.complete_graph.has_branch(105, 103)


def test_grid_add_tranformer(basic_grid: Grid):
    grid = basic_grid

    new_transformer_array = TransformerArray.zeros(1)
    new_transformer_array.from_node = 105
    new_transformer_array.to_node = 103

    assert 1 == len(grid.transformer)
    assert not grid.graphs.complete_graph.has_branch(105, 103)
    grid.add_branch(new_transformer_array)
    assert 2 == len(grid.transformer)
    assert EMPTY_ID not in grid.transformer.id
    assert grid.graphs.complete_graph.has_branch(105, 103)


def test_grid_delete_tranformer(basic_grid: Grid):
    grid = basic_grid

    transformer = grid.transformer.get(301)
    assert grid.graphs.complete_graph.has_branch(transformer.from_node.item(), transformer.to_node.item())

    grid.delete_branch(branch=transformer)

    assert 0 == len(grid.transformer)
    assert transformer.id not in grid.transformer.id

    assert not grid.graphs.complete_graph.has_branch(transformer.from_node.item(), transformer.to_node.item())


def test_grid_add_three_winding_transformer():
    grid = Grid.empty()
    nodes = NodeArray.zeros(3)
    nodes.id = [102, 103, 104]
    grid.append(nodes)

    three_winding_transformer = ThreeWindingTransformerArray.zeros(1)
    three_winding_transformer.node_1 = 102
    three_winding_transformer.node_2 = 103
    three_winding_transformer.node_3 = 104
    three_winding_transformer.status_1 = 1
    three_winding_transformer.status_2 = 1
    three_winding_transformer.status_3 = 1
    grid.append(three_winding_transformer)

    assert 1 == len(grid.three_winding_transformer)
    assert grid.graphs.active_graph.has_branch(102, 103)
    assert grid.graphs.active_graph.has_branch(102, 104)
    assert grid.graphs.active_graph.has_branch(103, 104)


def test_grid_delete_three_winding_transformer(grid_with_3wt: Grid):
    grid = grid_with_3wt
    assert grid.graphs.active_graph.has_branch(101, 102)
    assert grid.graphs.active_graph.has_branch(101, 103)
    assert grid.graphs.active_graph.has_branch(102, 103)

    grid.delete_branch3(branch=grid.three_winding_transformer[0])

    assert 0 == len(grid.three_winding_transformer)

    assert not grid.graphs.active_graph.has_branch(101, 102)
    assert not grid.graphs.active_graph.has_branch(101, 103)
    assert not grid.graphs.active_graph.has_branch(102, 103)


def test_grid_activate_branch(basic_grid: Grid):
    grid = basic_grid

    line = grid.line.get(203)
    assert line.from_status == 0 or line.to_status == 0

    assert not grid.graphs.active_graph.has_branch(line.from_node.item(), line.to_node.item())

    grid.make_active(branch=line)

    assert grid.graphs.active_graph.has_branch(line.from_node.item(), line.to_node.item())

    target_line_after = grid.line.get(203)
    assert target_line_after.from_status == 1
    assert target_line_after.to_status == 1


def test_grid_inactivate_branch(basic_grid: Grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line)

    target_line_after = grid.line.get(202)
    assert target_line_after.from_status == 1
    assert target_line_after.to_status == 0

    graph = grid.graphs.active_graph
    assert not graph.has_branch(target_line.from_node.item(), target_line.to_node.item())


def test_grid_make_inactive_from_side(basic_grid: Grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    # line 7 is expected to be active
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line, at_to_side=False)

    target_line_after = grid.line.get(202)
    assert 0 == target_line_after.from_status


def test_grid_make_inactive_to_side(basic_grid: Grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    # line 7 is expected to be active
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line)

    target_line_after = grid.line.get(202)
    assert 0 == target_line_after.to_status


def test_add_active_branch_to_extended_grid():
    """Test adding a branch to the custom grid"""
    grid = ExtendedGrid.empty()
    nodes = DefaultedCustomNodeArray.zeros(2)
    grid.append(nodes)

    line = DefaultedCustomLineArray.zeros(1)
    line.from_node = nodes[0].id
    line.to_node = nodes[1].id
    line.from_status = 1
    line.to_status = 1
    assert 0 == grid.line.size
    grid.append(line)
    assert 1 == grid.line.size
    assert 2 == len(grid.graphs.active_graph.external_ids)
