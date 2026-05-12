# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass
from typing import ClassVar

import numpy as np
from numpy._typing import NDArray

from power_grid_model_ds import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import CustomLineArray, CustomNodeArray, DefaultedCustomLineArray, DefaultedCustomNodeArray


class UserDefinedArray(FancyArray):
    """A user defined array that does not inherit from any existing grid array with id references."""

    branch_id: NDArray[np.int32]
    node_id: NDArray[np.int32]

    _id_columns: ClassVar[set[str]] = {"branch_id", "node_id"}
    _defaults: ClassVar[dict[str, int]] = {"branch_id": 42, "node_id": 43}


@dataclass
class ExtendedGrid(Grid):
    """ExtendedGrid class for testing purposes."""

    node: DefaultedCustomNodeArray
    line: DefaultedCustomLineArray
    user_defined: UserDefinedArray
    extra_value: int = 123


@dataclass
class ExtendedGridNoDefaults(Grid):
    node: CustomNodeArray
    line: CustomLineArray
