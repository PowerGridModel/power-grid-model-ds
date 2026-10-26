# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy
from dataclasses import dataclass

import pytest

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.constants import EMPTY_ID
from power_grid_model_ds._core.model.containers.base import FancyArrayContainer
from power_grid_model_ds._core.model.containers.helpers import container_equal
from power_grid_model_ds.arrays import LineArray, NodeArray
from tests.fixtures.grid_classes import ExtendedGrid
from tests.fixtures.grids import build_basic_grid


class TestContainerEqual:
    def test_grids_equal(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        assert container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_different_nodes(self, basic_grid: Grid):
        grid1 = basic_grid
        grid2 = deepcopy(grid1)
        # modify a node
        grid2.node.u_rated[0] += 1000.0
        assert not container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_different_type(self):
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = Grid.from_extended(grid1)
        assert not container_equal(grid1, grid2, fields_to_ignore=["graphs"])

    def test_ignore_extras(self):
        grid1 = build_basic_grid(ExtendedGrid.empty())
        grid2 = Grid.from_extended(grid1)
        assert container_equal(grid1, grid2, ignore_extras=True, fields_to_ignore=["graphs"])
        assert container_equal(grid1, grid2, ignore_extras=True)
        assert not container_equal(grid1, grid2, ignore_extras=False, fields_to_ignore=["graphs"])


@dataclass
class _NodeLineContainer(FancyArrayContainer):
    node: NodeArray
    line: LineArray


@pytest.fixture
def minimal_node_line_container() -> _NodeLineContainer:
    """Build a minimal grid to test recalculation of ids"""
    container = _NodeLineContainer.empty()
    nodes = NodeArray.empty(3)
    nodes.id = [1, 2, 9999]
    container.append(nodes, check_max_id=False)

    lines = LineArray.empty(3)
    lines.id = [100, 200, 300]
    lines.from_node = [1, 2, 9999]
    lines.to_node = [2, 9999, EMPTY_ID]
    container.append(lines, check_max_id=False)
    return container


class TestRecalculateIds:
    def test_recalculate_ids(self, minimal_node_line_container: _NodeLineContainer):
        assert minimal_node_line_container.ids == {1, 2, 100, 200, 300, 9999}
        assert minimal_node_line_container.max_id == 9999

        assert minimal_node_line_container.node.id.tolist() == [1, 2, 9999]
        assert minimal_node_line_container.node.feeder_branch_id.tolist() == [EMPTY_ID] * 3

        assert minimal_node_line_container.line.id.tolist() == [100, 200, 300]
        assert minimal_node_line_container.line.from_node.tolist() == [1, 2, 9999]
        assert minimal_node_line_container.line.to_node.tolist() == [2, 9999, EMPTY_ID]

        mapping = minimal_node_line_container.recalculate_ids()
        expected_mapping = {
            1: 1,
            2: 2,
            100: 3,
            200: 4,
            300: 5,
            9999: 6,
        }
        assert mapping == expected_mapping

        # Check that the ids have been recalculated correctly
        assert minimal_node_line_container.ids == {1, 2, 3, 4, 5, 6}
        assert minimal_node_line_container.max_id == 6

        # Check that the nodes have been updated to reflect the new ids
        assert minimal_node_line_container.node.id.tolist() == [1, 2, 6]
        assert minimal_node_line_container.node.feeder_branch_id.tolist() == [EMPTY_ID] * 3

        # Check that the lines have been updated to reflect the new line and node ids
        assert minimal_node_line_container.line.id.tolist() == [3, 4, 5]
        assert minimal_node_line_container.line.from_node.tolist() == [1, 2, 6]
        assert minimal_node_line_container.line.to_node.tolist() == [2, 6, EMPTY_ID]  # EMPTY is still EMPTY
