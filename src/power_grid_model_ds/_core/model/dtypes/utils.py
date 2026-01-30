# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from numpy.typing import NDArray

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.dtypes.appliances import SymLoad, SymGen, Source
from power_grid_model_ds._core.model.dtypes.branches import Link, Line, Transformer, GenericBranch, AsymLine, \
    ThreeWindingTransformer
from power_grid_model_ds._core.model.dtypes.nodes import Node
from power_grid_model_ds._core.model.dtypes.regulators import TransformerTapRegulator
from power_grid_model_ds._core.model.dtypes.sensors import SymPowerSensor, SymVoltageSensor, SymCurrentSensor, \
    AsymPowerSensor, AsymVoltageSensor, AsymCurrentSensor
from power_grid_model_ds._core.utils.misc import get_inherited_attrs

_PGM_DTYPES = (
    SymLoad,
    SymGen,
    Source,
    Node,
    Link,
    Line,
    Transformer,
    GenericBranch,
    AsymLine,
    ThreeWindingTransformer,
    TransformerTapRegulator,
    SymPowerSensor,
    SymVoltageSensor,
    SymCurrentSensor,
    AsymPowerSensor,
    AsymVoltageSensor,
    AsymCurrentSensor
)


def to_pgm_input_array(array: FancyArray) -> NDArray:
    """Convert to corresponding pgm array"""
    for dtype in _PGM_DTYPES:
        # Note: opted for issubclass instead of isinstance so .data is still understood by type checker
        if issubclass(array.__class__, dtype):
            return array.data[list(get_inherited_attrs(dtype).keys())]
    raise TypeError(f"{array.__class__.__name__} is not a PGM array")