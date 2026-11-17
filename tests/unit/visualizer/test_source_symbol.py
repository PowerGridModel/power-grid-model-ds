# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.parsers import _parse_appliances
from power_grid_model_ds.arrays import SourceArray, SymLoadArray


def _appliance(component_type, array_type, with_coords):
    array = array_type.zeros(1)
    array["id"] = 101
    array["node"] = 1
    array["status"] = 1
    node = {"data": {"id": "1", "group": "node", "associated_ids": {"node": [1]}}}
    if with_coords:
        node["position"] = {"x": 10.0, "y": 20.0}
    elements = {"1": node}
    _parse_appliances(elements, array, component_type)
    return elements


def test_source_keeps_original_edge_and_selectable_symbol():
    elements = _appliance(ComponentType.source, SourceArray, with_coords=True)
    edge = elements["101"]
    symbol = elements["101_ghost_node"]

    assert edge["data"]["source"] == "1"
    assert edge["data"]["target"] == "101_ghost_node"
    assert edge["data"]["associated_ids"] == {"source": [101]}
    assert "source" in edge["classes"].split()
    assert symbol["selectable"] is True
    assert symbol["data"]["associated_ids"] == {"source": [101]}
    assert symbol["data"]["group"] == "source_ghost_node"
    assert symbol["position"] == {"x": 130.0, "y": 20.0}


def test_source_without_coordinates_preserves_layout_control():
    elements = _appliance(ComponentType.source, SourceArray, with_coords=False)
    assert "position" not in elements["101_ghost_node"]


def test_other_appliance_unchanged():
    elements = _appliance(ComponentType.sym_load, SymLoadArray, with_coords=True)
    assert elements["101_ghost_node"]["selectable"] is False
    assert elements["101_ghost_node"]["position"] == {"x": 10.0, "y": 20.0}


def test_source_symbol_styles_exist():
    styles = {entry["selector"]: entry["style"] for entry in DEFAULT_STYLESHEET}
    symbol = styles['node[group = "source_ghost_node"]']
    assert symbol["background-image"].startswith("data:image/svg+xml,")
    assert "source-arrow-shape" in styles[".source"]
    assert styles[".source"]["source-arrow-shape"] == "none"
