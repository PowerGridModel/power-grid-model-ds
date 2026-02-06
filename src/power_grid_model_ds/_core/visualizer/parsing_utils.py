# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from power_grid_model_ds._core.model.arrays.base.array import FancyArray

PGM_ID_KEY = "pgm_id"


def array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """
    Stringify the record (required by Dash).
    Also, rename the "id" column to "pgm_id" to avoid conflicts with Dash's internal use of "id".
    """
    return {
        (PGM_ID_KEY if column == "id" else column): value for column, value in zip(columns, array_record.tolist().pop())
    }
