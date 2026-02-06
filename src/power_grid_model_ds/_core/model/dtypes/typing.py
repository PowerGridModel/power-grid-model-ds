# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Annotated, Literal, TypeVar

import numpy as np
from numpy.typing import NDArray

_DT = TypeVar("_DT", bound=np.generic)
NDArray3 = Annotated[NDArray[_DT], Literal[3]]
