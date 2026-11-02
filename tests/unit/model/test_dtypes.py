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
_PGM_COMPONENTS_NOT_IN_DS = set()
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

    for attr in array_dtype.fields:
        if attr not in pgm_dtype.fields:
            continue  # checked in test_ds_attributes_exist_in_pgm

        assert array_dtype[attr] == pgm_dtype[attr], (
            f"{array_class.__name__} dtype field '{attr}' does not match PGM dtype field '{attr}'"
        )


@pytest.mark.parametrize("component_type", list(_COMPONENT_TYPE_TO_ARRAY_CLASS.keys()))
def test_ds_attributes_exist_in_pgm(component_type: ComponentType):
    """
    Tests that every PGM-DS attribute is a valid PGM attribute, unless explicitly listed as DS-only.

    not missing_pgm_attributes: every DS attribute must be in the PGM dtype or explicitly listed as DS-only.
    This enforces DS attributes ⊆ (PGM attributes U DS-only attributes).

    not missing_ds_only_attributes: every entry in the DS-only list must still exist in the DS array.

    not pgm_ds_only_attributes: a DS-only attribute must not also exist in PGM; if it does, the exception list is stale.
    """
    array_class = _COMPONENT_TYPE_TO_ARRAY_CLASS[component_type]
    pgm_attribute_names = power_grid_meta_data[DatasetType.input][component_type].dtype.names
    assert pgm_attribute_names is not None
    pgm_attributes = set(pgm_attribute_names)
    ds_attributes = set(array_class.get_dtype().names)
    ds_only = _DS_ONLY_ATTRIBUTES.get(component_type, set())

    missing_pgm_attributes = ds_attributes - ds_only - pgm_attributes
    assert not missing_pgm_attributes, (
        f"{array_class.__name__} attributes {sorted(missing_pgm_attributes)} are not PGM attributes "
        f"of '{component_type.value}'. If they are DS-only, add to _DS_ONLY_ATTRIBUTES."
    )

    missing_ds_only_attributes = ds_only - ds_attributes
    assert not missing_ds_only_attributes, (
        f"Attributes {sorted(missing_ds_only_attributes)} specified in _DS_ONLY_ATTRIBUTES "
        f"are not in {array_class.__name__}"
    )

    # Check DS-only attributes are not already defined in PGM
    pgm_ds_only_attributes = ds_only & pgm_attributes
    assert not pgm_ds_only_attributes, (
        f"Attributes {sorted(pgm_ds_only_attributes)} specified in _DS_ONLY_ATTRIBUTES "
        f"already exists in PGM for '{component_type.value}'"
    )


@pytest.mark.parametrize("component_type", list(ComponentType))
def test_pgm_components_attributes_covered_by_ds(component_type: ComponentType):
    """
    Warns about PGM input attributes that are neither in the PGM-DS array nor explicitly skipped.

    not stale_skips: every skipped attribute must still exist in PGM.

    not included_skips: skipped attributes must still be absent from DS;
    remove them from the skip list once DS supports them.

    Warning for unskipped PGM attributes missing from DS. These may need to be added or skipped.
    """
    if component_type not in _COMPONENT_TYPE_TO_ARRAY_CLASS:
        if component_type not in _PGM_ATTRIBUTES_NOT_IN_DS:
            warnings.warn(
                f"PGM component {component_type.value} not modelled in DS. Please implement it or add in _SKIPPED_PGM_COMPONENTS",
                stacklevel=1,
            )
        return
    array_class = _COMPONENT_TYPE_TO_ARRAY_CLASS[component_type]
    ds_attributes = set(array_class.get_dtype().names)
    pgm_attribute_names = power_grid_meta_data[DatasetType.input][component_type].dtype.names
    assert pgm_attribute_names is not None
    pgm_attributes = set(pgm_attribute_names)
    skipped = {attribute.value for attribute in _PGM_ATTRIBUTES_NOT_IN_DS.get(component_type, set())}

    stale_skips = skipped - pgm_attributes
    assert not stale_skips, (
        f"Attributes {sorted(stale_skips)} specified in _PGM_ATTRIBUTES_NOT_IN_DS "
        f"are not PGM attributes of '{component_type.value}'"
    )

    included_skips = skipped & ds_attributes
    assert not included_skips, (
        f"Attributes {sorted(included_skips)} specified in _PGM_ATTRIBUTES_NOT_IN_DS "
        f"are now in {array_class.__name__}; remove them from the skip list"
    )

    missing_attributes = pgm_attributes - ds_attributes - skipped
    if missing_attributes:
        warnings.warn(
            f"PGM attributes {sorted(missing_attributes)} of '{component_type.value}' are missing in "
            f"{array_class.__name__}. Either implement them in PGM-DS or list them in _PGM_ATTRIBUTES_NOT_IN_DS.",
            stacklevel=1,
        )
