# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests a custom array container that inherits from Grid."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays import LineArray, NodeArray, TransformerArray
from power_grid_model_ds._core.model.grids.base import Grid

# pylint: disable=missing-class-docstring,attribute-defined-outside-init


class CustomLineArray(LineArray):
    extra_field: NDArray[np.int64]


class CustomTransformer(TransformerArray):
    extra_field: NDArray[np.int64]


@dataclass
class CustomGrid(Grid):
    line: CustomLineArray
    transformer: CustomTransformer


def test_add_active_branch():
    """Test adding a branch to the custom grid"""
    grid = CustomGrid.empty()
    nodes = NodeArray.zeros(2)
    grid.append(nodes)

    line = CustomLineArray.zeros(1)
    line["from_node"] = nodes["id"][0]
    line["to_node"] = nodes["id"][1]
    line["from_status"] = 1
    line["to_status"] = 1
    assert 0 == grid.line.size
    grid.append(line)
    assert 1 == grid.line.size
    assert 2 == len(grid.graphs.active_graph.external_ids)
