# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import (
    LineArray,
    LinkArray,
    NodeArray,
    SourceArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
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


class TestMergeGrids:
    def test_merge_two_grids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S11 12", "S11 13 link", "13 14 transformer")
        grid1_size = grid1.node.size
        grid2_size = grid2.node.size

        merged_grid = grid1.merge(grid2, mode="keep_ids")
        merged_grid_size = merged_grid.node.size

        assert merged_grid_size == grid1_size + grid2_size, "Merged grid size should be the sum of both grids' sizes"

    def test_merge_two_grids_with_overlapping_node_ids(self):
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 4 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")
        source = SourceArray(id=[501], node=[1], status=[1], u_ref=[0.0])
        grid1.append(source)
        grid2.append(source)

        merged_grid = grid1.merge(grid2, mode="recalculate_ids")
        assert merged_grid.check_ids() is None, "Asset ids are not unique after merging!"

        # Check if from and to nodes are updated by checking that their values form the entire set of node ids:
        assert set(merged_grid.branches.from_node).union(merged_grid.branches.to_node) == set(merged_grid.node.id), (
            "All from and to nodes should form the entire set of node ids in the merged grid!"
        )

        # assert node in grid.source is updated by checking if the node column contains values that are all node ids:
        assert set(merged_grid.source.node).issubset(merged_grid.node.id), "All source nodes should be valid node ids!"

    def test_merge_two_grids_with_overlapping_line(self):
        # Now both grids have 14 as highest node id, so both will have branch ids 15, 16 and 17:
        grid1 = Grid.from_txt("S1 2", "S1 3 link", "3 14 transformer")
        grid2 = Grid.from_txt("S1 2", "S1 13 link", "13 14 transformer")

        merged_grid = grid1.merge(grid2, mode="recalculate_ids")
        assert merged_grid.check_ids() is None, "Asset ids are not unique after merging!"
