# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy

import numpy as np
import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymGenArray,
    AsymLineArray,
    AsymLoadArray,
    BranchArray,
    GenericBranchArray,
    LineArray,
    LinkArray,
    NodeArray,
    ShuntArray,
    SourceArray,
    SymGenArray,
    SymLoadArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.constants import EMPTY_ID
from power_grid_model_ds._core.model.grids._modify import delete_appliance
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
    assert all(id in grid.node.id for id in (list(range(1002, 1009)) + list(range(2001, 2009))))

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
    assert all(id in grid.sym_power_sensor.id for id in range(22003, 22016))

    assert 12016 not in grid.asym_power_sensor.id
    assert all(id in grid.asym_power_sensor.id for id in range(22016, 22029))

    assert 12029 not in grid.sym_current_sensor.id
    assert all(id in grid.sym_current_sensor.id for id in range(22029, 22035))

    assert 12035 not in grid.asym_current_sensor.id
    assert all(id in grid.asym_current_sensor.id for id in range(22035, 22041))

    assert 13001 not in grid.voltage_regulator.id
    assert all(id in grid.voltage_regulator.id for id in range(23001, 23005))

    assert 13005 not in grid.transformer_tap_regulator.id
    assert all(id in grid.transformer_tap_regulator.id for id in [23005, 23006])

    remaining_branches = [
        (1001, 1002),
        (1001, 1003),
        (1001, 1004),
        (1001, 1005),
        (1001, 1006),
        (1001, 1007),
        (1001, 1008),
        (1007, 1008),
    ]
    for branch in remaining_branches:
        assert not grid.graphs.complete_graph.has_branch(*branch), f"Branch {branch} present"
    assert grid.graphs.complete_graph.nr_branches == len(remaining_branches)


@pytest.mark.parametrize(
    "branch_array_class,branch_id_to_delete,deleted_ids",
    [
        pytest.param(
            LineArray,
            10001,
            [10001, 12004, 12017, 12029, 12035],
            id="line",
        ),
        pytest.param(
            LinkArray,
            10002,
            [10002, 12005, 12018, 12030, 12036],
            id="link",
        ),
        pytest.param(
            AsymLineArray,
            10003,
            [10003, 12006, 12019, 12031, 12037],
            id="asym_line",
        ),
        pytest.param(
            GenericBranchArray,
            10004,
            [10004, 12007, 12020, 12032, 12038],
            id="generic_branch",
        ),
        pytest.param(
            TransformerArray,
            10005,
            [10005, 12008, 12021, 12033, 12039, 13005],
            id="transformer",
        ),
    ],
)
def test_grid_delete_branch_all(
    topologically_full_grid: Grid,
    branch_array_class,
    branch_id_to_delete: int,
    deleted_ids: list[int],
):
    grid = topologically_full_grid

    # Act
    branch_name = grid.find_array_field(branch_array_class).name
    target_branch = getattr(grid, branch_name).get(branch_id_to_delete)
    grid.delete_branch(branch=target_branch)

    # Check that none of the deleted IDs are present in any arrays
    for deleted_id in deleted_ids:
        assert deleted_id not in grid.sym_power_sensor.id
        assert deleted_id not in grid.asym_power_sensor.id
        assert deleted_id not in grid.sym_current_sensor.id
        assert deleted_id not in grid.asym_current_sensor.id
        assert deleted_id not in grid.transformer_tap_regulator.id
        assert deleted_id not in getattr(grid, branch_name).id

    assert len(grid.sym_power_sensor) == 25
    assert len(grid.asym_power_sensor) == 25
    assert len(grid.sym_current_sensor) == 11
    assert len(grid.asym_current_sensor) == 11
    if branch_array_class == TransformerArray:
        assert len(grid.transformer_tap_regulator) == 3
    else:
        assert len(grid.transformer_tap_regulator) == 4

    assert not grid.graphs.complete_graph.has_branch(target_branch.from_node.item(), target_branch.to_node.item())
    assert grid.graphs.complete_graph.nr_branches == 15


def test_grid_delete_branch3_all(topologically_full_grid: Grid):
    grid = topologically_full_grid
    deleted_ids = [10006, 12009, 12022, 12034, 12040, 13006]

    target_branch = grid.three_winding_transformer.get(10006)
    grid.delete_branch3(branch=target_branch)

    for deleted_id in deleted_ids:
        assert deleted_id not in grid.sym_power_sensor.id
        assert deleted_id not in grid.asym_power_sensor.id
        assert deleted_id not in grid.sym_current_sensor.id
        assert deleted_id not in grid.asym_current_sensor.id
        assert deleted_id not in grid.transformer_tap_regulator.id
        assert deleted_id not in grid.three_winding_transformer.id

    assert len(grid.sym_power_sensor) == 25
    assert len(grid.asym_power_sensor) == 25
    assert len(grid.sym_current_sensor) == 11
    assert len(grid.asym_current_sensor) == 11
    assert len(grid.transformer_tap_regulator) == 3

    for branch in [
        (target_branch.node_1.item(), target_branch.node_2.item()),
        (target_branch.node_2.item(), target_branch.node_3.item()),
        (target_branch.node_3.item(), target_branch.node_1.item()),
    ]:
        assert not grid.graphs.complete_graph.has_branch(*branch), f"Branch {branch} present"
    assert grid.graphs.complete_graph.nr_branches == 13


@pytest.mark.parametrize(
    "appliance_array_class,appliance_id_to_delete,deleted_ids",
    [
        pytest.param(
            SourceArray,
            11001,
            [11001, 12010, 12023],
            id="source",
        ),
        pytest.param(
            ShuntArray,
            11002,
            [11002, 12011, 12024],
            id="shunt",
        ),
        pytest.param(
            SymLoadArray,
            11003,
            [11003, 12012, 12025, 13001],
            id="sym_load",
        ),
        pytest.param(
            SymGenArray,
            11004,
            [11004, 12013, 12026, 13002],
            id="sym_gen",
        ),
        pytest.param(
            AsymLoadArray,
            11005,
            [11005, 12014, 12027, 13003],
            id="asym_load",
        ),
        pytest.param(
            AsymGenArray,
            11006,
            [11006, 12015, 12028, 13004],
            id="asym_gen",
        ),
    ],
)
def test_grid_delete_appliance_all(
    topologically_full_grid: Grid, appliance_array_class, appliance_id_to_delete: int, deleted_ids: list[int]
):
    grid = topologically_full_grid

    # Act
    appliance_name = grid.find_array_field(appliance_array_class).name
    target_appliance = getattr(grid, appliance_name).get(appliance_id_to_delete)

    # TODO - change test to grid.remove once implemented
    delete_appliance(grid, target_appliance)

    for deleted_id in deleted_ids:
        assert deleted_id not in grid.sym_power_sensor.id
        assert deleted_id not in grid.asym_power_sensor.id
        assert deleted_id not in grid.voltage_regulator.id
        assert deleted_id not in getattr(grid, appliance_name).id

    assert len(getattr(grid, appliance_name)) == 1
    assert len(grid.sym_power_sensor) == 25
    assert len(grid.asym_power_sensor) == 25
    if appliance_array_class in [SymLoadArray, SymGenArray, AsymLoadArray, AsymGenArray]:
        assert len(grid.voltage_regulator) == 7
    else:
        assert len(grid.voltage_regulator) == 8


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


class TestDeleteNodes:
    def test_delete_node_without_additional_properties(self, basic_grid: Grid):
        assert 106 in basic_grid.node.id
        assert 106 in basic_grid.transformer["to_node"]

        original_grid = deepcopy(basic_grid)
        node = basic_grid.node.get(id=106)
        basic_grid.delete_node(node)

        assert 106 not in basic_grid.transformer["to_node"]
        assert 106 not in basic_grid.node.id
        assert len(original_grid.node) == len(basic_grid.node) + 1
        assert len(original_grid.transformer) == len(basic_grid.transformer) + 1

    def test_delete_node_with_source(self, basic_grid: Grid):
        assert 101 in basic_grid.node.id
        assert 101 in basic_grid.source.node

        original_grid = deepcopy(basic_grid)
        node = basic_grid.node.get(id=101)
        basic_grid.delete_node(node)

        assert 101 not in basic_grid.node.id
        assert 101 not in basic_grid.source.node
        assert len(original_grid.node) == len(basic_grid.node) + 1
        assert len(original_grid.source) == len(basic_grid.source) + 1

    def test_delete_node_with_load(self, basic_grid: Grid):
        assert 102 in basic_grid.node.id
        assert 102 in basic_grid.sym_load.node

        original_grid = deepcopy(basic_grid)
        node = basic_grid.node.get(id=102)
        basic_grid.delete_node(node)

        assert 102 not in basic_grid.node.id
        assert 102 not in basic_grid.sym_load.node
        assert len(original_grid.node) == len(basic_grid.node) + 1
        assert len(original_grid.sym_load) == len(basic_grid.sym_load) + 1


class TestReverseBranches:
    def test_reverse_line(self, basic_grid: Grid):
        line = basic_grid.line.get(from_node=102, to_node=103)
        basic_grid.reverse_branches(line)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=102, to_node=103)

        new_line = basic_grid.line.get(from_node=103, to_node=102)

        assert new_line.from_node == line.to_node
        assert new_line.to_node == line.from_node
        assert new_line.id == line.id

    def test_reverse_branch(self, basic_grid: Grid):
        branch = basic_grid.branches.get(from_node=101, to_node=102)
        basic_grid.reverse_branches(branch)

        with pytest.raises(RecordDoesNotExist):
            basic_grid.line.get(from_node=101, to_node=102)

        new_branch = basic_grid.line.get(from_node=102, to_node=101)

        assert new_branch.from_node == branch.to_node
        assert new_branch.to_node == branch.from_node
        assert new_branch.id == branch.id

    def test_reverse_all_branches(self, basic_grid: Grid):
        from_nodes = basic_grid.branches.from_node
        to_nodes = basic_grid.branches.to_node

        basic_grid.reverse_branches(basic_grid.branches)

        assert np.all(from_nodes == basic_grid.branches.to_node)
        assert np.all(to_nodes == basic_grid.branches.from_node)

    def test_reverse_no_branches(self, basic_grid: Grid):
        basic_grid.reverse_branches(BranchArray())

    def test_reverse_statuses(self):
        grid = Grid.from_txt("101 102 open", "103 104")

        assert grid.branches.from_node.tolist() == [101, 103]
        assert grid.branches.from_status.tolist() == [1, 1]
        assert grid.branches.to_node.tolist() == [102, 104]
        assert grid.branches.to_status.tolist() == [0, 1]

        grid.reverse_branches(grid.branches)

        assert grid.branches.from_node.tolist() == [102, 104]
        assert grid.branches.from_status.tolist() == [0, 1]
        assert grid.branches.to_node.tolist() == [101, 103]
        assert grid.branches.to_status.tolist() == [1, 1]
