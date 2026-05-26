# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Base data types"""

from typing import Any, ClassVar

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.constants import empty


class Id:
    """Base dtype for id arrays"""

    _defaults: ClassVar[dict[str, Any]] = {"id": empty}
    _id_columns: ClassVar[set[str]] = {"id"}
    id: NDArray[np.int32]
