# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Optional dependencies for the arrays module."""

import importlib.util

HAS_PANDAS = importlib.util.find_spec("pandas") is not None
if HAS_PANDAS:
    import pandas as pd
else:
    pd = None  # pylint: disable=invalid-name

__all__ = ["pd"]
