# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import numpy as np
import pytest

from power_grid_model_ds import Grid


def test_grid_as_str(basic_grid: Grid):
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

    def test_from_txt_parallel_lines_without_ids(self):
        grid = Grid.from_txt("S1 2", "S1 2 open")
        assert grid.line.size == 2
        assert grid.line.id.tolist() == [3, 4]
        assert grid.line.from_status.tolist() == [1, 1]
        assert grid.line.to_status.tolist() == [1, 0]

    def test_from_txt_parallel_lines_with_ids(self):
        grid = Grid.from_txt("S1 2 12", "S1 2 120")
        assert grid.line.size == 2
        assert grid.line.id.tolist() == [12, 120]

    def test_from_txt_with_unordered_node_ids(self):
        grid = Grid.from_txt("S1 2", "S1 10", "10 11", "2 5", "5 6", "3 4", "3 7")
        assert 9 == grid.node.size

    def test_from_txt_with_unordered_branch_ids(self):
        grid = Grid.from_txt("5 6 16", "3 4 17", "3 7 18", "S1 2 12", "S1 10 13", "10 11 14", "2 5 15")
        assert 9 == grid.node.size

    def test_from_txt_file(self, tmp_path: Path):
        txt_file = tmp_path / "tmp_grid"
        txt_file.write_text("S1 2\nS1 3 open\n2 7\n3 5\n3 6 transformer\n5 7\n7 8\n8 9", encoding="utf-8")
        grid = Grid.from_txt_file(txt_file)
        txt_file.unlink()

        assert 8 == grid.node.size
        assert 1 == grid.branches.filter(to_status=0).size
        assert 1 == grid.transformer.size
        np.testing.assert_array_equal([14, 10, 11, 12, 13, 15, 16, 17], grid.branches.id)

    def test_from_txt_all_branch_types(self):
        grid = Grid.from_txt(
            "1 2 12",
            "2 3 link,23",
            "3 4 transformer,34",
            "4 5 generic_branch,45",
            "5 6 asym_line,56",
        )
        assert grid.line.id.tolist() == [12]
        assert grid.link.id.tolist() == [23]
        assert grid.transformer.id.tolist() == [34]
        assert grid.generic_branch.id.tolist() == [45]
        assert grid.asym_line.id.tolist() == [56]
