# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Grid tests"""

import dataclasses

import numpy as np
import pytest

from power_grid_model_ds._core.model.arrays import (
    LineArray,
    LinkArray,
    NodeArray,
    TransformerArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.constants import EMPTY_ID
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.grid_classes import ExtendedGrid

# pylint: disable=missing-function-docstring,missing-class-docstring


def test_initialize_empty_grid(grid):
    assert isinstance(grid, Grid)
    fields = dataclasses.asdict(grid).keys()
    assert {
        "link",
        "sym_load",
        "sym_power_sensor",
        "source",
        "_id_counter",
        "transformer_tap_regulator",
        "asym_voltage_sensor",
        "three_winding_transformer",
        "transformer",
        "node",
        "line",
        "sym_gen",
        "graphs",
        "sym_voltage_sensor",
    } == set(fields)


def test_initialize_empty_extended_grid():
    grid = ExtendedGrid.empty()
    assert isinstance(grid, ExtendedGrid)


def test_grid_build(basic_grid):
    grid = basic_grid

    # The grid consists of 6 nodes
    assert 6 == len(grid.node)
    # 1 of these is a source
    assert 1 == len(grid.source)
    # 4 of these have a load attaches
    assert 4 == len(grid.sym_load)

    inactive_mask = np.logical_or(grid.line.from_status == 0, grid.line.to_status == 0)
    inactive_lines = grid.line[inactive_mask]
    # we have placed 1 normally open point
    assert 1 == len(inactive_lines)

    # All nodes should be in both graphs
    assert len(grid.graphs.active_graph.external_ids) == len(grid.node)
    assert len(grid.graphs.complete_graph.external_ids) == len(grid.node)

    nr_branches = len(grid.line) + len(grid.transformer) + len(grid.link)
    assert nr_branches == grid.graphs.complete_graph.nr_branches
    assert nr_branches - 1 == grid.graphs.active_graph.nr_branches

    inactive_mask = np.logical_or(grid.line.from_status == 0, grid.line.to_status == 0)
    inactive_lines = grid.line[inactive_mask]
    # we have placed 1 normally open point
    assert 1 == len(inactive_lines)

    assert len(grid.line) + len(grid.transformer) + len(grid.link) - 1 == grid.graphs.active_graph.nr_branches
    assert len(grid.line) + len(grid.transformer) + len(grid.link) == grid.graphs.complete_graph.nr_branches


def test_grid_add_node(basic_grid):
    grid = basic_grid

    new_node = NodeArray.zeros(1)
    grid.add_node(node=new_node)

    assert 7 == len(grid.node)
    assert EMPTY_ID not in grid.node.id
    assert grid.node[-1].id.item() in grid.graphs.complete_graph.external_ids
    assert EMPTY_ID not in grid.graphs.complete_graph.external_ids


def test_grid_delete_node(basic_grid):
    grid = basic_grid

    target_node = grid.node.get(101)
    grid.delete_node(node=target_node)

    assert 5 == len(grid.node)
    assert target_node.id not in grid.node.id


# pylint: disable=no-member
def test_grid_add_line(basic_grid):
    grid = basic_grid

    line = LineArray.zeros(1)
    line.from_node = 102
    line.to_node = 105

    assert not grid.graphs.complete_graph.has_branch(102, 105)

    grid.add_branch(branch=line)

    assert 5 == len(grid.line)
    assert EMPTY_ID not in grid.line.id
    assert grid.graphs.complete_graph.has_branch(102, 105)


def test_grid_delete_line(basic_grid):
    grid = basic_grid

    line = grid.line.get(201)

    assert grid.graphs.complete_graph.has_branch(line.from_node.item(), line.to_node.item())

    grid.delete_branch(branch=line)

    assert 3 == len(grid.line)
    assert line.id not in grid.line.id

    assert not grid.graphs.complete_graph.has_branch(line.from_node.item(), line.to_node.item())


def test_grid_delete_inactive_line(basic_grid):
    grid = basic_grid

    inactive_mask = grid.line.from_status == 0
    target_line = grid.line[inactive_mask]

    assert grid.graphs.complete_graph.has_branch(target_line.from_node.item(), target_line.to_node.item())

    grid.delete_branch(branch=target_line)

    assert 3 == len(grid.line)
    assert target_line.id not in grid.line.id

    assert not grid.graphs.complete_graph.has_branch(target_line.from_node.item(), target_line.to_node.item())


def test_grid_delete_transformer_with_regulator(basic_grid):
    grid = basic_grid
    transformer_regulator = TransformerTapRegulatorArray.zeros(1)
    transformer_regulator.regulated_object = 301
    grid.append(transformer_regulator)

    assert 1 == len(grid.transformer_tap_regulator)

    transformer = grid.transformer.get(id=301)
    grid.delete_branch(branch=transformer)

    assert 0 == len(grid.transformer)
    assert transformer.id not in grid.transformer.id


def test_grid_add_link(basic_grid):
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


def test_grid_add_tranformer(basic_grid):
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


def test_grid_delete_tranformer(basic_grid):
    grid = basic_grid

    transformer = grid.transformer.get(301)
    assert grid.graphs.complete_graph.has_branch(transformer.from_node.item(), transformer.to_node.item())

    grid.delete_branch(branch=transformer)

    assert 0 == len(grid.transformer)
    assert transformer.id not in grid.transformer.id

    assert not grid.graphs.complete_graph.has_branch(transformer.from_node.item(), transformer.to_node.item())


def test_grid_activate_branch(basic_grid):
    grid = basic_grid

    line = grid.line.get(203)
    assert line.from_status == 0 or line.to_status == 0

    assert not grid.graphs.active_graph.has_branch(line.from_node.item(), line.to_node.item())

    grid.make_active(branch=line)

    assert grid.graphs.active_graph.has_branch(line.from_node.item(), line.to_node.item())

    target_line_after = grid.line.get(203)
    assert target_line_after.from_status == 1
    assert target_line_after.to_status == 1


def test_grid_inactivate_branch(basic_grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line)

    target_line_after = grid.line.get(202)
    assert target_line_after.from_status == 1
    assert target_line_after.to_status == 0

    graph = grid.graphs.active_graph
    assert not graph.has_branch(target_line.from_node.item(), target_line.to_node.item())


def test_grid_make_inactive_from_side(basic_grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    # line 7 is expected to be active
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line, at_to_side=False)

    target_line_after = grid.line.get(202)
    assert 0 == target_line_after.from_status


def test_grid_make_inactive_to_side(basic_grid):
    grid = basic_grid

    target_line = grid.line.get(202)
    # line 7 is expected to be active
    assert target_line.from_status == 1 and target_line.to_status == 1
    grid.make_inactive(branch=target_line)

    target_line_after = grid.line.get(202)
    assert 0 == target_line_after.to_status


def test_grid_as_str(basic_grid):
    grid = basic_grid

    grid_as_string = str(grid)

    assert "102 106 301,transformer" in grid_as_string
    assert "103 104 203,open" in grid_as_string


class TestFromTxt:
    def test_from_txt_lines(self):
        grid = Grid.from_txt(
            "S1 2",
            "S1 3 open",
            "2 7",
            "3 5",
            "3 6 transformer",
            "5 7",
            "7 8",
            "8 9",
        )
        assert 8 == grid.node.size
        assert 1 == grid.branches.filter(to_status=0).size
        assert 1 == grid.transformer.size
        np.testing.assert_array_equal([14, 10, 11, 12, 13, 15, 16, 17], grid.branches.id)

    def test_from_txt_string(self):
        txt_string = "S1 2\nS1 3 open\n2 7\n3 5\n3 6 transformer\n5 7\n7 8\n8 9"
        assert Grid.from_txt(txt_string)

    def test_from_txt_string_with_spaces(self):
        txt_string = "S1 2     \nS1 3   open\n2    7\n3 5\n   3 6 transformer\n5 7\n7   8\n8 9"
        assert Grid.from_txt(txt_string)

    def test_from_docstring(self):
        assert Grid.from_txt("""
        S1 2
        S1 3 open
        2 7
        3 5
        3 6 transformer
        5 7
        7 8
        8 9
        """)

    def test_from_txt_with_branch_ids(self):
        grid = Grid.from_txt(
            "S1 2 91", "S1 3 92,open", "2 7 93", "3 5 94", "3 6 transformer,95", "5 7 96", "7 8 97", "8 9 98"
        )
        assert 8 == grid.node.size
        assert 1 == grid.branches.filter(to_status=0).size
        assert 1 == grid.transformer.size
        np.testing.assert_array_equal([95, 91, 92, 93, 94, 96, 97, 98], grid.branches.id)

    def test_from_txt_with_conflicting_ids(self):
        with pytest.raises(ValueError):
            Grid.from_txt("S1 2", "1 3")

    def test_from_txt_with_invalid_line(self):
        with pytest.raises(ValueError):
            Grid.from_txt("S1")

    def test_from_txt_with_unordered_node_ids(self):
        grid = Grid.from_txt("S1 2", "S1 10", "10 11", "2 5", "5 6", "3 4", "3 7")
        assert 9 == grid.node.size

    def test_from_txt_with_unordered_branch_ids(self):
        grid = Grid.from_txt("5 6 16", "3 4 17", "3 7 18", "S1 2 12", "S1 10 13", "10 11 14", "2 5 15")
        assert 9 == grid.node.size

    def test_from_txt_file(self, tmp_path):
        txt_file = tmp_path / "tmp_grid"
        txt_file.write_text("S1 2\nS1 3 open\n2 7\n3 5\n3 6 transformer\n5 7\n7 8\n8 9", encoding="utf-8")
        grid = Grid.from_txt_file(txt_file)
        txt_file.unlink()

        assert 8 == grid.node.size
        assert 1 == grid.branches.filter(to_status=0).size
        assert 1 == grid.transformer.size
        np.testing.assert_array_equal([14, 10, 11, 12, 13, 15, 16, 17], grid.branches.id)
