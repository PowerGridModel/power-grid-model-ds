# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

try:
    from power_grid_model_ds._core.visualizer.app import visualize
except ImportError as error:
    raise ImportError(
        "Missing dependencies for visualizer: install with 'pip install power-grid-model-ds[visualizer]'"
    ) from error

__all__ = ["visualize"]
