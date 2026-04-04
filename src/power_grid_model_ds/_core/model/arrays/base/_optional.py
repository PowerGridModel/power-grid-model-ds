# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Optional dependencies for the arrays module."""

try:
    import pandas as pd
except ImportError:
    pd = None  # pylint: disable=invalid-name

__all__ = ["pd"]
