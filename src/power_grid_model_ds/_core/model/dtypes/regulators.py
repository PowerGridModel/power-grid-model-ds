# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.dtypes.id import Id


class Regulator(Id):
    "Regulator data type"

    regulated_object: NDArray[np.int32]  # a valid regulated object ID
    status: NDArray[np.int8]  # connection status of regulated object


class TransformerTapRegulator(Regulator):
    """Transformer tap regulator data type"""

    control_side: NDArray[np.int8]  # the controlled side of the transformer (see BranchSide/Branch3Side of PGM)
    u_set: NDArray[np.float64]  # the voltage setpoint
    u_band: NDArray[np.float64]  # the width of the voltage band
    line_drop_compensation_r: NDArray[np.float64]  # compensation for voltage drop due to resistance during transport
    line_drop_compensation_x: NDArray[np.float64]  # compensation for voltage drop due to reactance during transport

    _defaults = {
        "line_drop_compensation_r": 0,
        "line_drop_compensation_x": 0,
    }


class VoltageRegulator(Regulator):
    """Voltage regulator data type"""

    u_ref: NDArray[np.float64]  # the voltage setpoint
    q_max: NDArray[np.float64]  # the width of the voltage band
    q_min: NDArray[np.float64]  # compensation for voltage drop due to resistance during transport
