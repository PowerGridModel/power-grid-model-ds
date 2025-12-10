# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
"""Extended grid definition for testing purposes."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays import LineArray, TransformerArray
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
    extra_integer: int = 0


class CustomLineArrayDefaults(LineArray):
    extra_field: NDArray[np.int64]

    _defaults = {"extra_field": 42}


class CustomTransformerDefaults(TransformerArray):
    extra_field: NDArray[np.int64]

    _defaults = {"extra_field": 100}


@dataclass
class CustomGridWithDefaults(Grid):
    line: CustomLineArrayDefaults
    transformer: CustomTransformerDefaults
    extra_integer: int = 0
