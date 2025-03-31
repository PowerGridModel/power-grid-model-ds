# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html


def test_get_cytoscape_html():
    elements = [{"data": {"id": "1", "group": "node"}}]
    cyto_html = get_cytoscape_html("preset", elements)
    assert cyto_html.children.elements == elements
