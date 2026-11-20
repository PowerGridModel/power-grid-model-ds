# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for F05 scenario integration with the visualizer and component tables."""

from unittest.mock import patch

import pytest
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    OUTPUT_PREFIX,
    _get_y_data_for_cell_selection,
    display_selected_elements,
)
from power_grid_model_ds.visualizer import visualize


def make_grid():
    return Grid.from_txt("S1 2 12", "2 3 23")


def make_output_data():
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (2, 1))
    nodes["id"] = [[1], [1]]
    nodes["u"] = [[[401.0, 402.0, 403.0]], [[411.0, 412.0, 413.0]]]
    return {ComponentType.node: nodes}


def _select_node_one(scenario_index):
    tables = display_selected_elements([{"associated_ids": {"node": [1]}}], None, scenario_index)
    return tables[1]


def test_server_state_stores_timestamps():
    timestamps = ("2026-11-05T09:00:00+01:00",)
    server_state.set_app_state(make_grid(), timestamps=timestamps)
    assert server_state.get_timestamps() == timestamps


def test_server_state_resets_timestamps():
    server_state.set_app_state(make_grid(), timestamps=("2026-11-05T09:00:00+01:00",))
    server_state.set_app_state(make_grid())
    assert server_state.get_timestamps() is None


def test_visualize_passes_validated_timestamps_to_state():
    timestamps = ["2026-11-05T09:00:00+01:00", "2026-11-05T09:15:00+01:00"]
    with patch("power_grid_model_ds.visualizer.Dash") as dash:
        visualize(grid=make_grid(), output_data=make_output_data(), timestamps=timestamps)
    assert server_state.get_timestamps() == tuple(timestamps)
    dash.return_value.run.assert_called_once()


def test_visualize_rejects_mismatched_timestamp_count():
    with (
        patch("power_grid_model_ds.visualizer.Dash") as dash,
        pytest.raises(ValueError, match="timestamps"),
    ):
        visualize(
            grid=make_grid(),
            output_data=make_output_data(),
            timestamps=["2026-11-05T09:00:00+01:00"],
        )
    dash.assert_not_called()


def test_visualize_without_timestamps_preserves_existing_api():
    with patch("power_grid_model_ds.visualizer.Dash") as dash:
        visualize(grid=make_grid())
    assert server_state.get_timestamps() is None
    dash.return_value.run.assert_called_once()


def test_scenario_changes_selected_node_output_in_existing_table():
    server_state.set_app_state(make_grid(), output_data=make_output_data())
    first = _select_node_one(0)
    second = _select_node_one(1)
    assert first.rowData[0]["output__u"] == [401.0, 402.0, 403.0]
    assert second.rowData[0]["output__u"] == [411.0, 412.0, 413.0]
    assert first.id == {"type": "selection-table", "group": "node"}
    assert any(column["field"] == "output__u" for column in second.columnDefs)


def test_no_batch_data_keeps_base_component_table():
    server_state.set_app_state(make_grid())
    table = _select_node_one(None)
    assert table.rowData[0]["id"] == 1
    assert all(not column["field"].startswith(OUTPUT_PREFIX) for column in table.columnDefs)


def test_output_graph_column_resolves_to_output_dataset():
    server_state.set_app_state(make_grid(), output_data=make_output_data())
    x, y = _get_y_data_for_cell_selection(ComponentType.node, 1, "output__u")
    assert x.tolist() == [0, 1]
    assert y.tolist() == [[401.0, 402.0, 403.0], [411.0, 412.0, 413.0]]


def test_missing_component_output_preserves_base_table():
    server_state.set_app_state(make_grid(), output_data=make_output_data())
    table = display_selected_elements([{"associated_ids": {"node": [2]}}], None, 1)[1]
    assert table.rowData[0]["id"] == 2
    assert "output__u" not in table.rowData[0]
