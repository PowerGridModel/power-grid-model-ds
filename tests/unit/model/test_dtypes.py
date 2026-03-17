# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import pytest
from power_grid_model import ComponentType, DatasetType, power_grid_meta_data

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymCurrentSensorArray,
    AsymGenArray,
    AsymLineArray,
    AsymLoadArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    FaultArray,
    GenericBranchArray,
    LineArray,
    LinkArray,
    NodeArray,
    ShuntArray,
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


@pytest.mark.parametrize(
    "array_class, component_type",
    [
        (NodeArray, ComponentType.node),
        (LineArray, ComponentType.line),
        (TransformerArray, ComponentType.transformer),
        (AsymLineArray, ComponentType.asym_line),
        (LinkArray, ComponentType.link),
        (GenericBranchArray, ComponentType.generic_branch),
        (SymPowerSensorArray, ComponentType.sym_power_sensor),
        (AsymPowerSensorArray, ComponentType.asym_power_sensor),
        (SymVoltageSensorArray, ComponentType.sym_voltage_sensor),
        (AsymVoltageSensorArray, ComponentType.asym_voltage_sensor),
        (FaultArray, ComponentType.fault),
        (ShuntArray, ComponentType.shunt),
        (SymGenArray, ComponentType.sym_gen),
        (SymLoadArray, ComponentType.sym_load),
        (AsymGenArray, ComponentType.asym_gen),
        (AsymLoadArray, ComponentType.asym_load),
        (SymCurrentSensorArray, ComponentType.sym_current_sensor),
        (AsymCurrentSensorArray, ComponentType.asym_current_sensor),
        (VoltageRegulatorArray, ComponentType.voltage_regulator),
        (TransformerTapRegulatorArray, ComponentType.transformer_tap_regulator),
        (ThreeWindingTransformerArray, ComponentType.three_winding_transformer),
    ],
)
def test_pgm_dtypes(array_class, component_type):
    """Tests if dtypes of PGM-DS align with dtypes from PGM."""
    array_dtype = array_class.get_dtype()
    pgm_dtype = power_grid_meta_data[DatasetType.input][component_type].dtype

    assert array_dtype.fields is not None
    assert pgm_dtype.fields is not None

    for attr in array_dtype.fields:
        if attr not in pgm_dtype.fields:
            continue  # skip attributes that are not in PGM dtype, e.g., "node_type" and "feeder_*"

        # Check only dtype[0], skip full dtype. Offsets of PGM-DS are not same as PGM at the moment
        assert array_dtype.fields[attr][0] == pgm_dtype.fields[attr][0], (
            f"{array_class.__name__} dtype field '{attr}' does not match PGM dtype field '{attr}'"
        )
