# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Model constants"""

import numpy as np


def empty(dtype: type):
    """Returns the empty value for the given dtype."""
    if hasattr(dtype, "subdtype") and hasattr(dtype, "base"):  # special case for custom 'NDArray3' dtype
        dtype = dtype.base

    if np.issubdtype(dtype, np.str_):
        return ""
    if np.issubdtype(dtype, np.dtype("bool")):
        return False
    if np.issubdtype(dtype, np.floating):
        return np.nan
    try:
        return np.iinfo(dtype).min
    except ValueError as error:
        raise ValueError("Unsupported dtype") from error


EMPTY_ID = empty(np.int32)
