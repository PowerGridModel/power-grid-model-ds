# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Imports all the arrays, so that array can be imported as follows:
from power_grid_model_ds._core.model.arrays import MyArray
"""

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymCurrentSensorArray,
    AsymGenArray,
    AsymLineArray,
    AsymLoadArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    FaultArray,
    GenericBranchArray,
    IdArray,
    LineArray,
    LinkArray,
    NodeArray,
    ShuntArray,
    SourceArray,
    SymCurrentSensorArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
    VoltageRegulatorArray,
)

__all__ = [
    "AsymPowerSensorArray",
    "AsymVoltageSensorArray",
    "AsymCurrentSensorArray",
    "Branch3Array",
    "BranchArray",
    "GenericBranchArray",
    "FaultArray",
    "IdArray",
    "LineArray",
    "LinkArray",
    "NodeArray",
    "SourceArray",
    "ShuntArray",
    "SymLoadArray",
    "SymGenArray",
    "AsymGenArray",
    "AsymLoadArray",
    "SymCurrentSensorArray",
    "SymPowerSensorArray",
    "SymVoltageSensorArray",
    "AsymLineArray",
    "ThreeWindingTransformerArray",
    "TransformerArray",
    "TransformerTapRegulatorArray",
    "VoltageRegulatorArray",
]
