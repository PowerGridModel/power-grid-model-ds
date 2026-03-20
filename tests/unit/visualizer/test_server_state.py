# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state


@pytest.fixture(autouse=True)
def reset_server_state() -> None:
    """Reset module-level _state to a clean _AppState before every test."""
    server_state._state = server_state._AppState()


def test_server_state():
    assert server_state._state.grid is None

    test_grid_data = Grid.empty()
    server_state.set_grid(test_grid_data)
    assert server_state.get_grid() is test_grid_data


def test_get_grid_uninitialized():
    assert server_state._state.grid is None

    server_state.set_grid(None)

    with pytest.raises(RuntimeError, match="Grid state not initialized"):
        server_state.get_grid()
