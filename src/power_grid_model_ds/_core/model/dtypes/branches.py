# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Branch data types"""

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.id import Id


class BasicBranch(Id):
    """Branch that matches the PGM Branch data type"""

    from_node: NDArray[np.int32]  # node id (from-side)
    to_node: NDArray[np.int32]  # node id (to-side)
    from_status: NDArray[np.int8]  # 1 = closed, 0 = open
    to_status: NDArray[np.int8]  # 1 = closed, 0 = open


class Branch(BasicBranch):
    """PGM Branch with additional feeder information"""

    feeder_branch_id: NDArray[np.int32]  # branch id of the feeding branch
    feeder_node_id: NDArray[np.int32]  # node id of the feeding node
    is_feeder: NDArray[np.bool_]  # whether or not this branch is from the substation

    _defaults = {
        "feeder_branch_id": empty,
        "feeder_node_id": empty,
        "is_feeder": False,
    }


class BasicLink(BasicBranch):
    """Basic Link data type"""


class Link(Branch):
    """Link data type including feeder information"""


class BasicLine(BasicBranch):
    """Basic Line data type"""

    r1: NDArray[np.float64]  # serial resistance
    x1: NDArray[np.float64]  # serial reactance
    c1: NDArray[np.float64]  # shunt capacitance
    tan1: NDArray[np.float64]  # shunt loss factor
    i_n: NDArray[np.float64]  # rated current


class Line(Branch, BasicLine):
    """Line data type including feeder information"""


class BasicTransformer(BasicBranch):
    """Basic Transformer data type"""

    u1: NDArray[np.float64]  # rated voltage (from-side)
    u2: NDArray[np.float64]  # rated voltage (to-side)
    sn: NDArray[np.float64]  # rated power
    tap_size: NDArray[np.float64]  # size of each tap of the tap changer
    uk: NDArray[np.float64]  # relative short circuit voltage
    pk: NDArray[np.float64]  # short circuit loss
    i0: NDArray[np.float64]  # relative no-load current
    p0: NDArray[np.float64]  # no-load loss
    winding_from: NDArray[np.int8]  # winding type (from-side)
    winding_to: NDArray[np.int8]  # winding type (to-side)
    clock: NDArray[np.int8]  # clock number of phase shift
    tap_side: NDArray[np.int8]  # side of tap changer
    tap_pos: NDArray[np.int8]  # current position of tap changer
    tap_min: NDArray[np.int8]  # position of tap changer at minimum voltage
    tap_max: NDArray[np.int8]  # position of tap changer at maximum voltage
    tap_nom: NDArray[np.int8]  # nominal position of tap changer


class Transformer(Branch, BasicTransformer):
    """Transformer including feeder information"""


class Branch3(Id):
    """Branch3 data type"""

    node_1: NDArray[np.int32]
    node_2: NDArray[np.int32]
    node_3: NDArray[np.int32]
    status_1: NDArray[np.int8]
    status_2: NDArray[np.int8]
    status_3: NDArray[np.int8]


class ThreeWindingTransformer(Branch3):
    """ThreeWindingTransformer data type"""

    u1: NDArray[np.float64]
    u2: NDArray[np.float64]
    u3: NDArray[np.float64]
    sn_1: NDArray[np.float64]
    sn_2: NDArray[np.float64]
    sn_3: NDArray[np.float64]
    uk_12: NDArray[np.float64]
    uk_13: NDArray[np.float64]
    uk_23: NDArray[np.float64]
    pk_12: NDArray[np.float64]
    pk_13: NDArray[np.float64]
    pk_23: NDArray[np.float64]
    i0: NDArray[np.float64]
    p0: NDArray[np.float64]
    winding_1: NDArray[np.int8]
    winding_2: NDArray[np.int8]
    winding_3: NDArray[np.int8]
    clock_12: NDArray[np.int8]
    clock_13: NDArray[np.int8]
    tap_side: NDArray[np.int8]
    tap_pos: NDArray[np.int8]
    tap_min: NDArray[np.int8]
    tap_max: NDArray[np.int8]
    tap_nom: NDArray[np.int8]
    tap_size: NDArray[np.float64]
    uk_12_min: NDArray[np.float64]
    uk_13_min: NDArray[np.float64]
    uk_23_min: NDArray[np.float64]
    pk_12_min: NDArray[np.float64]
    pk_13_min: NDArray[np.float64]
    pk_23_min: NDArray[np.float64]
    uk_12_max: NDArray[np.float64]
    uk_13_max: NDArray[np.float64]
    uk_23_max: NDArray[np.float64]
    pk_12_max: NDArray[np.float64]
    pk_13_max: NDArray[np.float64]
    pk_23_max: NDArray[np.float64]
