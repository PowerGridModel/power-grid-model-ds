# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.dtypes.id import Id


class Fault(Id):
    "Fault data type"

    fault_object: NDArray[np.int32]  # a valid fault object ID, ie a node
    status: NDArray[np.int8]  # connection status of fault
    fault_type: NDArray[np.int8]  # type of fault (e.g. single line to ground, line to line, etc.)
    fault_phase: NDArray[np.int8]  # the phase(s) affected by the fault (e.g. A, B, C, AB, BC, AC, ABC)
    r_f: NDArray[np.float64]  # the fault resistance
    x_f: NDArray[np.float64]  # the fault reactance
