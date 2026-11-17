# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for two-winding transformer visual elements."""

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import (
    BRANCH_WIDTH,
    DEFAULT_STYLESHEET,
)
from power_grid_model_ds._core.visualizer.layout.transformer_rendering import prepare_transformer_rendering
from power_grid_model_ds._core.visualizer.transformer_constants import (
    TRANSFORMER_CIRCLE_RADIUS,
    TRANSFORMER_OPEN_CLASS,
    TRANSFORMER_OPEN_FROM_CLASS,
    TRANSFORMER_OPEN_TO_CLASS,
    TRANSFORMER_STROKE_WIDTH,
)


def _elements(target_y: float = 0) -> list[dict]:
    return [
        {"data": {"id": "n1"}, "position": {"x": 0, "y": 0}},
        {"data": {"id": "n2"}, "position": {"x": 300, "y": target_y}},
        {
            "data": {
                "id": "t1",
                "group": "transformer",
                "source": "n1",
                "target": "n2",
                "associated_ids": {"transformer": [123]},
            },
            "classes": "transformer",
        },
    ]


def test_horizontal_transformer_preserves_original_and_adds_symbol():
    original = _elements()
    result = prepare_transformer_rendering(original)
    assert len(original) == 3
    assert len(result) == 6
    assert result[2]["data"]["id"] == "t1"
    assert "transformer-original-hidden" in result[2]["classes"]
    symbol = next(e for e in result if e["data"].get("group") == "transformer_symbol")
    assert symbol["position"] == {"x": 150, "y": 0}
    assert symbol["data"]["associated_ids"] == {"transformer": [123]}
    assert symbol["selectable"] is True
    assert symbol["grabbable"] is True
    connections = [e for e in result if e["data"].get("visual_only") and "source" in e["data"]]
    assert {(e["data"]["source"], e["data"]["target"]) for e in connections} == {
        ("n1", symbol["data"]["id"]),
        (symbol["data"]["id"], "n2"),
    }
    assert all(e["selectable"] is False for e in connections)


def test_diagonal_transformer_has_rotated_symbol_and_preserved_connections():
    original = _elements(target_y=600)
    result = prepare_transformer_rendering(original)
    symbol = next(e for e in result if e["data"].get("group") == "transformer_symbol")
    assert symbol["position"] == {"x": 150, "y": 300}
    assert round(symbol["data"]["symbol_angle"], 2) == 63.43
    assert "transformer-original-hidden" in result[2]["classes"]
    assert symbol["grabbable"] is True
    assert symbol["selectable"] is True
    assert symbol["data"]["associated_ids"] == {"transformer": [123]}
    assert len([e for e in result if e["data"].get("visual_only") and "source" in e["data"]]) == 2


def test_too_short_transformer_is_unchanged():
    original = _elements()
    original[1]["position"]["x"] = 70
    assert prepare_transformer_rendering(original) == original


def test_three_winding_group_is_unchanged():
    original = _elements()
    original[2]["data"]["group"] = "three_winding_transformer"
    assert prepare_transformer_rendering(original) == original


def _visual_connections(classes: str) -> list[dict]:
    elements = _elements(target_y=600)
    elements[2]["classes"] = classes
    rendered = prepare_transformer_rendering(elements)
    return [e for e in rendered if e["data"].get("visual_only") and "source" in e["data"]]


def test_open_from_dashes_both_segments_but_marks_only_from_terminal():
    edges = _visual_connections("branch transformer open_branch open_branch_from")
    assert all(TRANSFORMER_OPEN_CLASS in edge["classes"] for edge in edges)
    assert TRANSFORMER_OPEN_FROM_CLASS in edges[0]["classes"]
    assert TRANSFORMER_OPEN_TO_CLASS not in edges[1]["classes"]


def test_open_to_dashes_both_segments_but_marks_only_to_terminal():
    edges = _visual_connections("branch transformer open_branch open_branch_to")
    assert all(TRANSFORMER_OPEN_CLASS in edge["classes"] for edge in edges)
    assert TRANSFORMER_OPEN_FROM_CLASS not in edges[0]["classes"]
    assert TRANSFORMER_OPEN_TO_CLASS in edges[1]["classes"]


def test_both_open_dashes_both_and_marks_both_terminals():
    edges = _visual_connections("branch transformer open_branch open_branch_from open_branch_to")
    assert all(TRANSFORMER_OPEN_CLASS in edge["classes"] for edge in edges)
    assert TRANSFORMER_OPEN_FROM_CLASS in edges[0]["classes"]
    assert TRANSFORMER_OPEN_TO_CLASS in edges[1]["classes"]


def test_closed_transformer_connections_remain_solid():
    edges = _visual_connections("branch transformer")
    assert all(TRANSFORMER_OPEN_CLASS not in edge["classes"] for edge in edges)


def test_open_style_is_dashed_and_marker_rules_are_preserved():
    rules = {rule["selector"]: rule["style"] for rule in DEFAULT_STYLESHEET}
    assert rules[f".{TRANSFORMER_OPEN_CLASS}"]["line-style"] == "dashed"
    assert rules[f".{TRANSFORMER_OPEN_FROM_CLASS}"]["source-arrow-shape"] == "diamond"
    assert rules[f".{TRANSFORMER_OPEN_TO_CLASS}"]["target-arrow-shape"] == "diamond"


def test_transformer_endpoints_remain_draggable():
    original = _elements(target_y=600)
    result = prepare_transformer_rendering(original)

    assert result[0].get("grabbable", True) is True
    assert result[1].get("grabbable", True) is True


def test_symbol_geometry_matches_branch_visual_weight():
    assert TRANSFORMER_CIRCLE_RADIUS >= 30
    assert TRANSFORMER_STROKE_WIDTH == BRANCH_WIDTH


def test_canvas_overlay_presentation_styles_are_single_source():
    rules = {rule["selector"]: rule["style"] for rule in DEFAULT_STYLESHEET}
    symbol = rules[".transformer-symbol"]
    connection = rules[".transformer-visual-connection"]
    assert symbol["background-opacity"] == 0
    assert symbol["background-image-opacity"] == 0
    assert connection["opacity"] == 0
    assert connection["width"] == TRANSFORMER_STROKE_WIDTH
