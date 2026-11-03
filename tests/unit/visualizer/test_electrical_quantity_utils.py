# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for electrical quantity extraction from batch results."""

import numpy as np
import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer.electrical_quantity_utils import (
    extract_scenario_values,
    get_scenario_count,
)


def test_scenario_count_without_output():
    assert get_scenario_count(None) == 0
    assert get_scenario_count({}) == 0


def test_scenario_count_with_batch_output():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (3, 2))

    output_data = {ComponentType.node: nodes}

    assert get_scenario_count(output_data) == 3


def test_extract_voltage_for_selected_scenario():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 3))

    nodes["id"] = [
        [11, 12, 13],
        [11, 12, 13],
    ]
    nodes["u_pu"] = [
        [0.98, 1.00, 1.02],
        [0.97, 0.99, 1.01],
    ]

    output_data = {ComponentType.node: nodes}

    result = extract_scenario_values(
        output_data,
        ComponentType.node,
        "u_pu",
        scenario_index=1,
    )

    assert result == {11: 0.97, 12: 0.99, 13: 1.01}


def test_extract_values_with_reordered_component_ids():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 3))

    nodes["id"] = [
        [11, 12, 13],
        [13, 11, 12],
    ]
    nodes["u_pu"] = [
        [0.98, 1.00, 1.02],
        [1.03, 0.97, 0.99],
    ]

    result = extract_scenario_values(
        {ComponentType.node: nodes},
        ComponentType.node,
        "u_pu",
        scenario_index=1,
    )

    assert result == {13: 1.03, 11: 0.97, 12: 0.99}


def test_extract_values_with_missing_and_nonfinite_results():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (1, 4))

    nodes["id"] = [[11, 12, 13, 14]]
    nodes["u_pu"] = [[0.98, np.nan, np.inf, 1.02]]

    result = extract_scenario_values(
        {ComponentType.node: nodes},
        ComponentType.node,
        "u_pu",
        scenario_index=0,
    )

    assert result == {11: 0.98, 14: 1.02}


def test_extract_values_for_missing_component_type():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (1, 1))
    nodes["id"] = [[11]]
    nodes["u_pu"] = [[1.0]]

    result = extract_scenario_values(
        {ComponentType.node: nodes},
        ComponentType.line,
        "loading",
        scenario_index=0,
    )

    assert result == {}


def test_extract_three_phase_voltage():
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (1, 2))

    nodes["id"] = [[11, 12]]
    nodes["u_pu"] = [
        [
            [0.98, 0.99, 1.00],
            [1.01, 1.02, 1.03],
        ]
    ]

    result = extract_scenario_values(
        {ComponentType.node: nodes},
        ComponentType.node,
        "u_pu",
        scenario_index=0,
        phase_index=1,
    )

    assert result == {11: 0.99, 12: 1.02}


def test_three_phase_values_require_phase_selection():
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (1, 1))

    with pytest.raises(ValueError, match="explicit phase index"):
        extract_scenario_values(
            {ComponentType.node: nodes},
            ComponentType.node,
            "u_pu",
            scenario_index=0,
        )


def test_invalid_scenario_index():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))

    with pytest.raises(IndexError, match="Scenario index"):
        extract_scenario_values(
            {ComponentType.node: nodes},
            ComponentType.node,
            "u_pu",
            scenario_index=2,
        )


def test_scalar_attribute_rejects_phase_selection():
    nodes = initialize_array(DatasetType.sym_output, ComponentType.node, (1, 1))

    with pytest.raises(ValueError, match="scalar"):
        extract_scenario_values(
            {ComponentType.node: nodes},
            ComponentType.node,
            "u_pu",
            scenario_index=0,
            phase_index=0,
        )


def test_duplicate_component_ids_are_rejected():
    nodes = initialize_array(
        DatasetType.sym_output,
        ComponentType.node,
        (1, 2),
    )

    nodes["id"] = [[11, 11]]
    nodes["u_pu"] = [[0.98, 1.02]]

    with pytest.raises(ValueError, match="Duplicate component ID 11"):
        extract_scenario_values(
            {ComponentType.node: nodes},
            ComponentType.node,
            "u_pu",
            scenario_index=0,
        )
