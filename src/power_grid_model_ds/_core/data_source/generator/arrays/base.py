# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Base generator"""

import numpy as np

from power_grid_model_ds._core.model.grids.base import Grid


class BaseGenerator:
    """Base class to build a generator for grid elements"""

    def __init__(self, grid: Grid, seed: int | None) -> None:
        """Initializes generator with grid and amount"""
        self.grid = grid

        self.starting_seed = seed
        self.rng = np.random.default_rng(seed)

    def reset_rng(self, seed: int):
        """Sets the rng for a generator"""
        rng = np.random.default_rng(seed)
        self.rng = rng
