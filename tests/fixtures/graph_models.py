# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel


class CustomTestGraphModel(RustworkxGraphModel):
    """Graph model used to verify custom graph model selection."""
