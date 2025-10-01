# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Branch data types"""

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.id import Id


class Branch(Id):
    """Branch data type"""

    from_node: NDArray[np.int32]  # node id (from-side)
    to_node: NDArray[np.int32]  # node id (to-side)
    from_status: NDArray[np.int8]  # 1 = closed, 0 = open
    to_status: NDArray[np.int8]  # 1 = closed, 0 = open
    feeder_branch_id: NDArray[np.int32]  # branch id of the feeding branch
    feeder_node_id: NDArray[np.int32]  # node id of the feeding node
    is_feeder: NDArray[np.bool_]  # whether or not this branch is from the substation

    _defaults = {
        "feeder_branch_id": empty,
        "feeder_node_id": empty,
        "is_feeder": False,
    }


class Link(Branch):
    """Link data type"""


class Line(Branch):
    """Line data type"""

    r1: NDArray[np.float64]  # serial resistance
    x1: NDArray[np.float64]  # serial reactance
    c1: NDArray[np.float64]  # shunt capacitance
    tan1: NDArray[np.float64]  # shunt loss factor
    i_n: NDArray[np.float64]  # rated current


class GenericBranch(Branch):
    """GenericBranch data type (generic_branch in power-grid-model)

    Off-nominal ratio k and phase shift theta are modelled explicitly. Rated power sn optional.
    The impedance (r1, x1) and admittance (g1, b1) are given wrt the to-side.
    """

    r1: NDArray[np.float64]  # positive-sequence resistance
    x1: NDArray[np.float64]  # positive-sequence reactance
    g1: NDArray[np.float64]  # positive-sequence conductance
    b1: NDArray[np.float64]  # positive-sequence susceptance
    k: NDArray[np.float64]  # off-nominal ratio
    theta: NDArray[np.float64]  # angle shift (radian)
    sn: NDArray[np.float64]  # rated power

    _defaults = {
        "k": 1.0,
        "theta": 0.0,
        "sn": 0.0,
    }


class Transformer(Branch):
    """Transformer data type"""

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


class AsymLine(Branch):
    """Asymmetric Line data type (asym_line in power-grid-model)

    Supports 3 or 4 phase (with neutral) resistance / reactance matrices and optional capacitance matrix
    or sequence capacitances c0/c1. If c_* matrix is omitted, c0 & c1 may be specified instead.
    Only include fields; validation logic handled elsewhere (not implemented here yet).
    """

    # Resistance matrix entries (series)
    r_aa: NDArray[np.float64]
    r_ba: NDArray[np.float64]
    r_bb: NDArray[np.float64]
    r_ca: NDArray[np.float64]
    r_cb: NDArray[np.float64]
    r_cc: NDArray[np.float64]
    r_na: NDArray[np.float64]  # optional neutral
    r_nb: NDArray[np.float64]
    r_nc: NDArray[np.float64]
    r_nn: NDArray[np.float64]

    # Reactance matrix entries (series)
    x_aa: NDArray[np.float64]
    x_ba: NDArray[np.float64]
    x_bb: NDArray[np.float64]
    x_ca: NDArray[np.float64]
    x_cb: NDArray[np.float64]
    x_cc: NDArray[np.float64]
    x_na: NDArray[np.float64]
    x_nb: NDArray[np.float64]
    x_nc: NDArray[np.float64]
    x_nn: NDArray[np.float64]

    # Capacitance matrix entries (shunt) optional
    c_aa: NDArray[np.float64]
    c_ba: NDArray[np.float64]
    c_bb: NDArray[np.float64]
    c_ca: NDArray[np.float64]
    c_cb: NDArray[np.float64]
    c_cc: NDArray[np.float64]

    # Alternative sequence capacitances
    c0: NDArray[np.float64]
    c1: NDArray[np.float64]

    i_n: NDArray[np.float64]  # rated current

    _defaults = {
        "r_na": empty,
        "r_nb": empty,
        "r_nc": empty,
        "r_nn": empty,
        "x_na": empty,
        "x_nb": empty,
        "x_nc": empty,
        "x_nn": empty,
        "c_aa": empty,
        "c_ba": empty,
        "c_bb": empty,
        "c_ca": empty,
        "c_cb": empty,
        "c_cc": empty,
        "c0": empty,
        "c1": empty,
        "i_n": empty,
    }
