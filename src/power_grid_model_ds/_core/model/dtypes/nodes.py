# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Node data types"""

from typing import ClassVar

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.id import Id
from power_grid_model_ds._core.model.enums.nodes import NodeType


class Node(Id):
    """Node data type"""

    u_rated: NDArray[np.float64]  # rated line-line voltage
    node_type: NDArray[np.int8]
    feeder_branch_id: NDArray[np.int32]  # branch id of the feeder
    feeder_node_id: NDArray[np.int32]  # node id of the first substation node

    _defaults: ClassVar = {
        "node_type": NodeType.UNSPECIFIED.value,
        "feeder_branch_id": empty,
        "feeder_node_id": empty,
    }
