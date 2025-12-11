# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import CustomLineArray, CustomNodeArray, DefaultedCustomLineArray, DefaultedCustomNodeArray


@dataclass
class ExtendedGrid(Grid):
    """ExtendedGrid class for testing purposes."""

    node: DefaultedCustomNodeArray
    line: DefaultedCustomLineArray
    extra_value: int = 123


@dataclass
class ExtendedGridNoDefaults(Grid):
    node: CustomNodeArray
    line: CustomLineArray
