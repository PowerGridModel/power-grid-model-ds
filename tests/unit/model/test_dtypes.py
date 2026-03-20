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

_COMPONENT_TYPE_TO_ARRAY_CLASS = {
    ComponentType.node: NodeArray,
    ComponentType.shunt: ShuntArray,
    ComponentType.line: LineArray,
    ComponentType.link: LinkArray,
    ComponentType.fault: FaultArray,
    ComponentType.generic_branch: GenericBranchArray,
    ComponentType.asym_line: AsymLineArray,
    ComponentType.asym_load: AsymLoadArray,
    ComponentType.asym_power_sensor: AsymPowerSensorArray,
    ComponentType.asym_current_sensor: AsymCurrentSensorArray,
    ComponentType.asym_voltage_sensor: AsymVoltageSensorArray,
    ComponentType.transformer: TransformerArray,
    ComponentType.transformer_tap_regulator: TransformerTapRegulatorArray,
    ComponentType.voltage_regulator: VoltageRegulatorArray,
    ComponentType.asym_gen: AsymGenArray,
    ComponentType.sym_current_sensor: SymCurrentSensorArray,
    ComponentType.sym_power_sensor: SymPowerSensorArray,
    ComponentType.sym_voltage_sensor: SymVoltageSensorArray,
    ComponentType.three_winding_transformer: ThreeWindingTransformerArray,
    ComponentType.sym_gen: SymGenArray,
    ComponentType.sym_load: SymLoadArray,
    ComponentType.source: SourceArray,
}


@pytest.mark.parametrize("component_type", list(ComponentType))
def test_pgm_dtypes(component_type: ComponentType):
    """Tests if dtypes of PGM-DS align with dtypes from PGM."""
    array_class = _COMPONENT_TYPE_TO_ARRAY_CLASS[component_type]
    array_dtype = array_class.get_dtype()
    pgm_dtype = power_grid_meta_data[DatasetType.input][component_type].dtype

    assert array_dtype.fields is not None, f"{array_class.__name__} dtype does not have fields"
    assert pgm_dtype.fields is not None, f"PGM dtype for component type '{component_type.value}' does not have fields"

    for attr in array_dtype.fields:
        if attr not in pgm_dtype.fields:
            continue  # skip attributes that are not in PGM dtype, e.g., "node_type" and "feeder_*"

        assert array_dtype[attr] == pgm_dtype[attr], (
            f"{array_class.__name__} dtype field '{attr}' does not match PGM dtype field '{attr}'"
        )
