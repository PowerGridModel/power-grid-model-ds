# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Node data types"""

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.id import Id
from power_grid_model_ds._core.model.enums.nodes import NodeType


class BasicNode(Id):
    """Basic Node that matches the PGM Node data type"""

    u_rated: NDArray[np.float64]  # rated line-line voltage


class Node(BasicNode):
    """Node data type, including node type and feeder information"""

    node_type: NDArray[np.int8]
    feeder_branch_id: NDArray[np.int32]  # branch id of the feeder
    feeder_node_id: NDArray[np.int32]  # node id of the first substation node

    _defaults = {
        "node_type": NodeType.UNSPECIFIED.value,
        "feeder_branch_id": empty,
        "feeder_node_id": empty,
    }
