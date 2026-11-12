# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for the F05 optional scenario-selection interface."""

from dash import dcc, html
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.layout.scenario_selection import (
    get_scenario_selection_html,
)

TIMESTAMPS = (
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
)


def make_output_data():
    """Create two scenarios with different component ordering."""
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (2, 2))
    nodes["id"] = [[10, 20], [20, 10]]
    nodes["u"] = [
        [[101.0, 102.0, 103.0], [201.0, 202.0, 203.0]],
        [[211.0, 212.0, 213.0], [111.0, 112.0, 113.0]],
    ]
    return {ComponentType.node: nodes}


def configure_state(timestamps=TIMESTAMPS, output_data=None):
    """Configure the visualizer state used by the layout."""
    server_state.set_app_state(
        grid=None,
        output_data=output_data,
        timestamps=timestamps,
    )


def _walk(component):
    """Walk the Dash component tree."""
    if isinstance(component, (list, tuple)):
        for child in component:
            yield from _walk(child)
        return

    if component is None or not hasattr(component, "to_plotly_json"):
        return

    yield component
    yield from _walk(getattr(component, "children", None))


def _component_by_id(panel, component_id):
    """Find a component by its Dash ID."""
    return next(component for component in _walk(panel) if getattr(component, "id", None) == component_id)


def test_selector_hidden_without_batch_data():
    """No scenario controls are shown when batch data is unavailable."""
    configure_state(timestamps=None)

    panel = get_scenario_selection_html()

    assert isinstance(panel, html.Div)
    assert panel.id == "timestamp-selection-container"
    assert not panel.children


def test_selector_is_numeric_and_initially_empty():
    """Scenario selection starts empty and allows numeric entry."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    selector = _component_by_id(panel, "scenario-selector")

    assert isinstance(selector, dcc.Input)
    assert selector.type == "number"
    assert selector.value is None
    assert selector.step == 1
    assert selector.placeholder == "e.g. 0"
    assert selector.debounce is False
    assert selector.style == {"width": "100%"}


def test_selector_has_no_browser_range_constraints():
    """Python validation handles out-of-range scenario indices."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    selector = _component_by_id(panel, "scenario-selector")

    props = selector.to_plotly_json()["props"]
    assert "min" not in props
    assert "max" not in props


def test_clear_button_is_removed():
    """Clearing the numeric field does not require a separate button."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    component_ids = {getattr(component, "id", None) for component in _walk(panel)}

    assert "scenario-clear" not in component_ids


def test_validation_message_is_available():
    """The layout exposes a target for scenario-index validation."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    validation = _component_by_id(panel, "scenario-validation")

    assert isinstance(validation, html.Div)
    assert "Enter a scenario index" in validation.children


def test_timestamp_controls_are_initially_empty():
    """Timestamp metadata must not automatically activate a scenario."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    date_picker = _component_by_id(panel, "timestamp-date")
    time_selector = _component_by_id(panel, "timestamp-time")

    assert isinstance(date_picker, dcc.DatePickerSingle)
    assert date_picker.date is None

    assert isinstance(time_selector, dcc.Dropdown)
    assert time_selector.value is None
    assert time_selector.options == []


def test_selector_available_without_timestamp_metadata():
    """Scenario selection works without timestamp metadata."""
    configure_state(timestamps=None, output_data=make_output_data())

    panel = get_scenario_selection_html()
    components = list(_walk(panel))
    selector = _component_by_id(panel, "scenario-selector")

    assert isinstance(selector, dcc.Input)
    assert selector.value is None
    assert selector.placeholder == "e.g. 0"

    assert not any(getattr(component, "id", None) in {"timestamp-date", "timestamp-time"} for component in components)


def test_no_duplicate_component_state_cards():
    """The scenario panel does not render redundant component-state cards."""
    configure_state(output_data=make_output_data())

    panel = get_scenario_selection_html()
    component_ids = {
        getattr(component, "id", None) for component in _walk(panel) if isinstance(getattr(component, "id", None), str)
    }

    assert "scenario-state-output" not in component_ids


def test_selector_does_not_require_timestamps():
    """A batch without timestamps still exposes the scenario selector."""
    configure_state(timestamps=None, output_data=make_output_data())

    panel = get_scenario_selection_html()

    selector = _component_by_id(panel, "scenario-selector")
    assert selector.type == "number"
    assert selector.value is None
    assert selector.step == 1
    assert "scenario-clear" not in {getattr(component, "id", None) for component in _walk(panel)}
