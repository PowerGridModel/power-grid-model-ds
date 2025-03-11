# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import sys
import unittest

from tests.fixtures.arrays import FancyTestArray


@unittest.skipUnless("pandas" in sys.modules, "pandas is not installed")
def test_as_df(fancy_test_array: FancyTestArray):
    """Test that .as_df() can convert an array to a pandas DataFrame."""
    data_frame = fancy_test_array.as_df()
    # pylint: disable=import-outside-toplevel, import-error
    import pandas

    assert isinstance(data_frame, pandas.DataFrame)
