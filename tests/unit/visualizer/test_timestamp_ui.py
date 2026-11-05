"""Tests for the F05 timestamp selector and component cards."""

from dash import dcc, html
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks.timestamp_selection import (
    _selected_components,
    build_timestamp_state,
)
from power_grid_model_ds._core.visualizer.layout.timestamp_selection import (
    get_timestamp_selection_html,
)

TIMESTAMPS = (
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
)


def make_output_data():
    nodes = initialize_array(DatasetType.asym_output, ComponentType.node, (2, 2))
    nodes["id"] = [[10, 20], [20, 10]]
    nodes["u"] = [
        [[101.0, 102.0, 103.0], [201.0, 202.0, 203.0]],
        [[211.0, 212.0, 213.0], [111.0, 112.0, 113.0]],
    ]
    return {ComponentType.node: nodes}


def configure_state(timestamps=TIMESTAMPS, output_data=None):
    server_state.set_app_state(
        grid=None,
        output_data=output_data,
        timestamps=timestamps,
    )


def _walk(component):
    """Walk Dash component trees without depending on their layout positions."""
    if isinstance(component, (list, tuple)):
        for child in component:
            yield from _walk(child)
        return

    if component is None or not hasattr(component, "to_plotly_json"):
        return

    yield component
    yield from _walk(getattr(component, "children", None))


def _text(component):
    """Collect visible text from a Dash component tree."""
    if isinstance(component, (list, tuple)):
        return " ".join(_text(child) for child in component)
    if not hasattr(component, "children"):
        return "" if component is None else str(component)
    return _text(component.children)


def _attribute_text(panel, attribute):
    """Return the text of the matching attribute card."""
    for component in _walk(panel):
        if getattr(component, "data-attribute", None) == attribute:
            return _text(component)
    raise AssertionError(f"Attribute {attribute!r} not displayed")


def test_selector_hidden_without_timestamp_metadata():
    configure_state(timestamps=None)
    panel = get_timestamp_selection_html()
    assert panel.id == "timestamp-selection-container"
    assert not panel.children


def test_selector_uses_source_timestamps():
    configure_state()
    panel = get_timestamp_selection_html()
    selector = next(
        component
        for component in _walk(panel)
        if isinstance(component, dcc.Dropdown) and component.id == "timestamp-selector"
    )
    assert selector.value == 0
    assert selector.options == [{"label": timestamp, "value": index} for index, timestamp in enumerate(TIMESTAMPS)]


def test_selected_components_are_unique():
    selection = [
        {"associated_ids": {"node": [10, 10, 20]}},
        {"associated_ids": {"node": [10]}},
    ]
    assert _selected_components(selection, None) == [
        (ComponentType.node, 10),
        (ComponentType.node, 20),
    ]


def test_selected_components_ignore_unrecognised_groups():
    assert _selected_components(
        [{"associated_ids": {"branches": [10], "node": [20]}}],
        None,
    ) == [(ComponentType.node, 20)]


def test_panel_uses_compact_empty_state():
    configure_state(output_data=make_output_data())
    panel = build_timestamp_state(0, None, None)
    assert isinstance(panel, html.Div)
    assert "No component selected" in _text(panel)
    assert "Select a network component to inspect its state." not in _text(panel)


def test_panel_rejects_invalid_scenario():
    configure_state(output_data=make_output_data())
    assert build_timestamp_state(99, None, None) == "Select an available timestamp."


def test_panel_displays_component_without_redundant_timestamp():
    configure_state(output_data=make_output_data())
    panel = build_timestamp_state(
        1,
        [{"associated_ids": {"node": [10]}}],
        None,
    )
    assert isinstance(panel, html.Div)
    assert "Node - ID 10" in _text(panel)
    assert "Selected timestamp:" not in _text(panel)


def test_panel_shows_missing_component_result():
    configure_state(output_data=make_output_data())
    panel = build_timestamp_state(
        0,
        [{"associated_ids": {"node": [999]}}],
        None,
    )
    assert "Component result unavailable" in _text(panel)


def test_timestamp_change_updates_three_phase_values():
    configure_state(output_data=make_output_data())
    selected = [{"associated_ids": {"node": [10]}}]

    first = build_timestamp_state(0, selected, None)
    second = build_timestamp_state(1, selected, None)

    assert "101.0" in _attribute_text(first, "u")
    assert "102.0" in _attribute_text(first, "u")
    assert "103.0" in _attribute_text(first, "u")
    assert "111.0" in _attribute_text(second, "u")
    assert "112.0" in _attribute_text(second, "u")
    assert "113.0" in _attribute_text(second, "u")


def test_component_lookup_uses_id_after_batch_reordering():
    configure_state(output_data=make_output_data())
    selected = [{"associated_ids": {"node": [20]}}]

    first = build_timestamp_state(0, selected, None)
    second = build_timestamp_state(1, selected, None)

    assert "201.0" in _attribute_text(first, "u")
    assert "211.0" in _attribute_text(second, "u")


def test_nonfinite_output_value_is_marked_unavailable():
    output_data = make_output_data()
    output_data[ComponentType.node]["u"][0, 0, 1] = float("nan")
    configure_state(output_data=output_data)

    panel = build_timestamp_state(
        0,
        [{"associated_ids": {"node": [10]}}],
        None,
    )
    assert "Unavailable (non-finite value)" in _attribute_text(panel, "u")


def test_output_and_update_data_remain_separate():
    output_data = make_output_data()
    updates = initialize_array(DatasetType.update, ComponentType.node, (2, 1))
    updates["id"] = [[10], [10]]

    server_state.set_app_state(
        grid=None,
        output_data=output_data,
        update_data={ComponentType.node: updates},
        timestamps=TIMESTAMPS,
    )

    panel = build_timestamp_state(
        1,
        [{"associated_ids": {"node": [10]}}],
        None,
    )

    component = panel.children[0]
    output_section = component.children[1]
    update_section = component.children[2]

    assert "Output data" in _text(output_section)
    assert "Update data" in _text(update_section)
    assert "111.0" in _text(output_section)
    assert "10" in _text(update_section)


def test_unavailable_attributes_are_collapsed():
    configure_state(output_data=make_output_data())
    panel = build_timestamp_state(
        0,
        [{"associated_ids": {"node": [10]}}],
        None,
    )

    details = [component for component in _walk(panel) if isinstance(component, html.Details)]
    assert details
    assert "Unavailable attributes" in _text(details[0])
