# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model import ComponentType

BRANCHES_COMPONENTS = [
    ComponentType.line.value,
    ComponentType.link.value,
    ComponentType.generic_branch.value,
    ComponentType.transformer.value,
    ComponentType.asym_line.value,
]

_HEADER_COMMON_OPTIONS = [
    {"label": ComponentType.node.value, "value": ComponentType.node.value},
    {"label": ComponentType.line.value, "value": ComponentType.line.value},
    {"label": ComponentType.link.value, "value": ComponentType.link.value},
    {"label": ComponentType.transformer.value, "value": ComponentType.transformer.value},
    {"label": ComponentType.three_winding_transformer.value, "value": ComponentType.three_winding_transformer.value},
    {"label": ComponentType.asym_line.value, "value": ComponentType.asym_line.value},
    {"label": ComponentType.generic_branch.value, "value": ComponentType.generic_branch.value},
    {"label": ComponentType.sym_load.value, "value": ComponentType.sym_load.value},
    {"label": ComponentType.sym_gen.value, "value": ComponentType.sym_gen.value},
    {"label": ComponentType.source.value, "value": ComponentType.source.value},
    {"label": "branches", "value": "branches"},
]

HEADER_HEATMAP_OPTIONS = _HEADER_COMMON_OPTIONS

HEADER_SEARCH_OPTIONS = _HEADER_COMMON_OPTIONS + [
    {"label": ComponentType.sym_power_sensor.value, "value": ComponentType.sym_power_sensor.value},
    {"label": ComponentType.asym_power_sensor.value, "value": ComponentType.asym_power_sensor.value},
    {"label": ComponentType.sym_voltage_sensor.value, "value": ComponentType.sym_voltage_sensor.value},
    {"label": ComponentType.asym_voltage_sensor.value, "value": ComponentType.asym_voltage_sensor.value},
    {"label": ComponentType.sym_current_sensor.value, "value": ComponentType.sym_current_sensor.value},
    {"label": ComponentType.asym_current_sensor.value, "value": ComponentType.asym_current_sensor.value},
    {"label": ComponentType.transformer_tap_regulator.value, "value": ComponentType.transformer_tap_regulator.value},
]


def _update_column_options(selected_group, columns):
    """Update the column dropdown options based on the selected group."""
    if not selected_group or not columns:
        return [], None

    # Get columns for the selected group (node, line, link, or transformer)
    columns = columns.get(selected_group, [])
    default_value = columns[0] if columns else "id"

    return columns, default_value
