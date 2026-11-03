# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for resetting electrical quantity colouring."""

from copy import deepcopy

from power_grid_model_ds._core.visualizer.callbacks.config import update_appliances
from power_grid_model_ds._core.visualizer.electrical_quantity_styling import clear_electrical_colors
from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass


def _node(node_id: int, *, substation: bool = False) -> dict:
    """Create a minimal Cytoscape node."""
    classes = "node substation_node" if substation else "node"

    return {
        "data": {
            "id": str(node_id),
            "group": "node",
            "associated_ids": {"node": [node_id]},
        },
        "classes": classes,
    }


def _line(line_id: int) -> dict:
    """Create a minimal Cytoscape branch."""
    return {
        "data": {
            "id": str(line_id),
            "group": "line",
            "associated_ids": {"line": [line_id]},
        },
        "classes": "branch",
    }


def _parsed_elements() -> dict:
    """Create a graph containing a previously coloured node."""
    node = _node(1)
    node["data"]["electrical_color"] = "#DE2D26"
    node["data"]["electrical_value"] = 1.05
    return {"node-1": node}


def _assert_default_node(element: dict) -> None:
    """Check that a normal node has its default display colour."""
    assert element["data"]["electrical_color"] == CYTO_COLORS[StyleClass.NODE.value]
    assert "electrical_value" not in element["data"]


def test_clearing_quantity_restores_default_colours():
    """Clearing Quantity restores the default appearance and legend."""
    elements, legend = update_appliances(
        show_appliances=False,
        quantity="none",
        scenario_index=0,
        parsed_elements=_parsed_elements(),
    )

    assert len(elements) == 1
    _assert_default_node(elements[0])
    assert legend == "No electrical quantity selected."


def test_clearing_scenario_restores_default_colours():
    """Clearing Scenario removes the active electrical visualisation."""
    elements, legend = update_appliances(
        show_appliances=False,
        quantity="u_pu",
        scenario_index=None,
        parsed_elements=_parsed_elements(),
    )

    assert len(elements) == 1
    _assert_default_node(elements[0])
    assert legend == "Select a scenario to display electrical values."


def test_initial_empty_selection():
    """Both dropdowns can start without an active selection."""
    elements, legend = update_appliances(
        show_appliances=False,
        quantity=None,
        scenario_index=None,
        parsed_elements=_parsed_elements(),
    )

    assert len(elements) == 1
    _assert_default_node(elements[0])
    assert legend == "No electrical quantity selected."


def test_reset_removes_electrical_value():
    """Reset removes the result value and restores the node colour."""
    parsed_elements = _parsed_elements()

    elements, legend = update_appliances(
        show_appliances=False,
        quantity="u_pu",
        scenario_index=None,
        parsed_elements=parsed_elements,
    )

    assert len(elements) == 1
    _assert_default_node(elements[0])
    assert legend == "Select a scenario to display electrical values."

    # The source graph must not be modified.
    assert parsed_elements["node-1"]["data"]["electrical_color"] == "#DE2D26"
    assert parsed_elements["node-1"]["data"]["electrical_value"] == 1.05


def test_reset_restores_default_node_color():
    node = _node(1)
    node["data"]["electrical_color"] = "#DE2D26"
    node["data"]["electrical_value"] = 1.05

    original = deepcopy(node)
    updated = clear_electrical_colors([node])

    _assert_default_node(updated[0])
    assert node == original


def test_reset_restores_substation_color():
    node = _node(16, substation=True)
    node["data"]["electrical_color"] = "#3182BD"

    updated = clear_electrical_colors([node])

    assert updated[0]["data"]["electrical_color"] == CYTO_COLORS["substation_node"]
    assert "electrical_value" not in updated[0]["data"]


def test_reset_does_not_modify_branch():
    branch = _line(18)

    updated = clear_electrical_colors([branch])

    assert updated == [branch]
    assert "electrical_color" not in updated[0]["data"]


def test_reset_preserves_topology():
    """Reset must not change element IDs, classes, or associations."""
    elements = [_node(1), _line(18)]

    elements[0]["data"]["electrical_color"] = "#DE2D26"
    elements[0]["data"]["electrical_value"] = 1.05

    updated = clear_electrical_colors(elements)

    assert len(updated) == len(elements)

    for original, restored in zip(elements, updated, strict=True):
        assert restored["data"]["id"] == original["data"]["id"]
        assert restored["data"]["associated_ids"] == original["data"]["associated_ids"]
        assert restored["classes"] == original["classes"]
