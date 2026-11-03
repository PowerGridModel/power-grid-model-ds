# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import warnings

import pytest
from power_grid_model import AttributeType, ComponentType, DatasetType, power_grid_meta_data

from power_grid_model_ds.arrays import (
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


_FEEDER_ATTRIBUTES = {"feeder_branch_id", "feeder_node_id", "is_feeder"}

# Attributes that only exist in PGM-DS (not in PGM). Any other DS attribute must exist in PGM.
_DS_ONLY_ATTRIBUTES: dict[ComponentType, set[str]] = {
    ComponentType.node: {"node_type", "feeder_branch_id", "feeder_node_id"},
    ComponentType.line: _FEEDER_ATTRIBUTES,
    ComponentType.link: _FEEDER_ATTRIBUTES,
    ComponentType.generic_branch: _FEEDER_ATTRIBUTES,
    ComponentType.asym_line: _FEEDER_ATTRIBUTES,
    ComponentType.transformer: _FEEDER_ATTRIBUTES,
}

# PGM input attributes that are (currently) intentionally not included in PGM-DS.
# Attributes missing from both the DS array and this mapping only trigger a warning.
_PGM_COMPONENTS_NOT_IN_DS: set[ComponentType] = set()
_PGM_ATTRIBUTES_NOT_IN_DS: dict[ComponentType, set[AttributeType]] = {
    ComponentType.shunt: {AttributeType.g0, AttributeType.b0},
    ComponentType.line: {AttributeType.r0, AttributeType.x0, AttributeType.c0, AttributeType.tan0},
    ComponentType.generic_branch: {AttributeType.k, AttributeType.theta, AttributeType.sn},
    ComponentType.asym_line: {
        AttributeType.r_na,
        AttributeType.r_nb,
        AttributeType.r_nc,
        AttributeType.r_nn,
        AttributeType.x_na,
        AttributeType.x_nb,
        AttributeType.x_nc,
        AttributeType.x_nn,
        AttributeType.c_aa,
        AttributeType.c_ba,
        AttributeType.c_bb,
        AttributeType.c_ca,
        AttributeType.c_cb,
        AttributeType.c_cc,
    },
    ComponentType.transformer: {
        AttributeType.i0_zero_sequence,
        AttributeType.p0_zero_sequence,
        AttributeType.uk_min,
        AttributeType.uk_max,
        AttributeType.pk_min,
        AttributeType.pk_max,
        AttributeType.r_grounding_from,
        AttributeType.x_grounding_from,
        AttributeType.r_grounding_to,
        AttributeType.x_grounding_to,
    },
    ComponentType.voltage_regulator: {AttributeType.q_min, AttributeType.q_max},
    ComponentType.three_winding_transformer: {
        AttributeType.r_grounding_1,
        AttributeType.x_grounding_1,
        AttributeType.r_grounding_2,
        AttributeType.x_grounding_2,
        AttributeType.r_grounding_3,
        AttributeType.x_grounding_3,
    },
    ComponentType.source: {
        AttributeType.u_ref_angle,
        AttributeType.sk,
        AttributeType.rx_ratio,
        AttributeType.z01_ratio,
    },
}


@pytest.mark.parametrize("component_type", list(_COMPONENT_TYPE_TO_ARRAY_CLASS.keys()))
def test_pgm_dtypes(component_type: ComponentType):
    """Tests if dtypes of PGM-DS align with dtypes from PGM."""
    array_class = _COMPONENT_TYPE_TO_ARRAY_CLASS[component_type]
    array_dtype = array_class.get_dtype()
    pgm_dtype = power_grid_meta_data[DatasetType.input][component_type].dtype

    assert array_dtype.fields is not None, f"{array_class.__name__} dtype does not have fields"
    assert pgm_dtype.fields is not None, f"PGM dtype for component type '{component_type.value}' does not have fields"

    # Compare dtypes only for shared attributes; attribute coverage is checked separately.
    for attr in array_dtype.fields:
        if attr not in pgm_dtype.fields:
            continue  # Checked in test_pgm_attributes_are_in_ds_or_skipped.

        assert array_dtype[attr] == pgm_dtype[attr], (
            f"{array_class.__name__} dtype field '{attr}' does not match PGM dtype field '{attr}'"
        )


@pytest.mark.parametrize("component_type", list(ComponentType))
def test_pgm_components_are_in_ds_or_skipped(component_type: ComponentType):
    """
    Warn for PGM components not modelled in DS unless they are explicitly skipped.

    A skipped component that becomes modelled in DS is stale and must be removed from the skip set.
    """
    if component_type not in _PGM_COMPONENTS_NOT_IN_DS:
        warnings.warn(
            f"PGM component '{component_type.value}' is not modelled in DS. "
            "Implement it or add it to _PGM_COMPONENTS_NOT_IN_DS if intentionally unsupported.",
            stacklevel=1,
        )
        return
    assert component_type in _COMPONENT_TYPE_TO_ARRAY_CLASS


@pytest.mark.parametrize("component_type", list(_COMPONENT_TYPE_TO_ARRAY_CLASS.keys()))
def test_pgm_attributes_are_in_ds_or_skipped(component_type: ComponentType):
    """
    Warn for PGM attributes not yet modelled in DS unless they are explicitly skipped.

    Warn for PGM attributes - DS attributes - skipped attributes, because PGM fields may arrive
    before PGM-DS supports them. A skipped attribute that is now in DS is stale and must be removed.
    """
    array_class = _COMPONENT_TYPE_TO_ARRAY_CLASS[component_type]
    ds_attribute_names = array_class.get_dtype().names
    pgm_attribute_names = power_grid_meta_data[DatasetType.input][component_type].dtype.names

    assert ds_attribute_names is not None, f"{array_class.__name__} dtype does not have named fields"
    assert pgm_attribute_names is not None, f"PGM dtype for '{component_type.value}' does not have named fields"

    ds_attributes = set(ds_attribute_names)
    pgm_attributes = set(pgm_attribute_names)
    ds_only_attributes = _DS_ONLY_ATTRIBUTES.get(component_type, set())
    skipped_attributes = {attribute.value for attribute in _PGM_ATTRIBUTES_NOT_IN_DS.get(component_type, set())}

    skipped_attributes_in_ds = skipped_attributes & ds_attributes
    assert not skipped_attributes_in_ds, (
        f"Attributes {sorted(skipped_attributes_in_ds)} in _PGM_ATTRIBUTES_NOT_IN_DS "
        f"are now in {array_class.__name__}; remove the stale entries"
    )

    attributes_yet_to_implement = pgm_attributes - ds_attributes - skipped_attributes
    if attributes_yet_to_implement:
        warnings.warn(
            f"PGM attributes {sorted(attributes_yet_to_implement)} of '{component_type.value}' are missing in "
            f"{array_class.__name__}. Implement them in PGM-DS or list them in _PGM_ATTRIBUTES_NOT_IN_DS.",
            stacklevel=1,
        )

    unexpected_ds_attributes = ds_attributes - pgm_attributes - ds_only_attributes
    assert not unexpected_ds_attributes, (
        f"{array_class.__name__} attributes {sorted(unexpected_ds_attributes)} are not in PGM "
        f"or _DS_ONLY_ATTRIBUTES for '{component_type.value}'"
    )

    stale_ds_only_attributes = ds_only_attributes - ds_attributes
    assert not stale_ds_only_attributes, (
        f"Attributes {sorted(stale_ds_only_attributes)} in _DS_ONLY_ATTRIBUTES "
        f"are not in {array_class.__name__}; remove the stale entries"
    )
