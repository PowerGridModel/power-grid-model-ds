# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Annotated, Literal, TypeVar

import numpy as np
from numpy.typing import NDArray

# define structural arrays with 3 values for 3-phase variables
# based on https://stackoverflow.com/a/72585748
_DT = TypeVar("_DT", bound=np.generic)
NDArray3 = Annotated[NDArray[_DT], Literal[3]]
