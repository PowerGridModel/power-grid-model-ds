# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
from numpy._typing import NDArray

from power_grid_model_ds._core.model.arrays import LineArray, NodeArray
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.dtypes.sensors import NDArray3


class FancyTestArray(FancyArray):
    """Test array with some attributes"""

    id: NDArray[np.int32]
    test_int: NDArray[np.int64]
    test_float: NDArray[np.float64]
    test_str: NDArray[np.str_]
    test_bool: NDArray[np.bool_]


class DefaultedFancyTestArray(FancyTestArray):
    """Test array with some defaulted attributes"""

    _defaults = {"id": -1, "test_int": 4, "test_float": 4.5, "test_str": "DEFAULT", "test_bool": True}


class DifferentFancyTestArray(FancyArray):
    """Test array with some different attributes"""

    id: NDArray[np.int64]
    test_int: NDArray[np.int64]
    test_float: NDArray[np.float64]
    test_str: NDArray[np.object_]
    test_bool: NDArray[np.bool_]
    test_bool2: NDArray[np.bool_]


class LongColumnNameFancyTestArray(FancyArray):
    """Test array with a very long column name"""

    this_is_a_very_long_column_name: NDArray[np.int64]
    this_is_a_very_long_column_name2: NDArray[np.int64]


class FancyNonIdArray(FancyArray):
    """Test array without an id column"""

    test_int: NDArray[np.int64]
    test_float: NDArray[np.float64]
    test_str: NDArray[np.str_]
    test_bool: NDArray[np.bool_]


class FancyTestArray3(FancyArray):
    """Test array with 3-phase attributes"""

    test_float1: NDArray3[np.float64]
    test_float2: NDArray3[np.float64]


class ExtendedNodeArray(NodeArray):
    """Extends the node array with an output value"""

    _defaults = {"u": 0}

    u: NDArray[np.float64]


class ExtendedLineArray(LineArray):
    """Extends the line array with an output value"""

    _defaults = {"i_from": 0}

    i_from: NDArray[np.float64]
