# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for the retained graph layout."""

from dash import dcc, html

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_GRAPH_HTML,
)


def _find_component(component, component_id):
    """Find a component by its Dash ID."""
    if getattr(component, "id", None) == component_id:
        return component

    children = getattr(component, "children", None)

    if children is None:
        return None

    if not isinstance(children, (list, tuple)):
        children = [children]

    for child in children:
        if not isinstance(child, (dcc.Store, dcc.Graph, html.Div, html.Button)):
            continue

        result = _find_component(child, component_id)

        if result is not None:
            return result

    return None


def test_retained_graph_store_exists():
    store = _find_component(
        SELECTION_GRAPH_HTML,
        "retained-graph-selections",
    )

    assert isinstance(store, dcc.Store)
    assert store.data == []
    assert store.storage_type == "memory"


def test_retained_graph_container_exists():
    container = _find_component(
        SELECTION_GRAPH_HTML,
        "retained-graphs-container",
    )

    assert isinstance(container, html.Div)


def test_clear_graphs_button_exists():
    button = _find_component(
        SELECTION_GRAPH_HTML,
        "clear-retained-graphs",
    )

    assert isinstance(button, html.Button)


def test_existing_graph_is_preserved():
    graph = _find_component(
        SELECTION_GRAPH_HTML,
        "selection-graph",
    )

    assert isinstance(graph, dcc.Graph)
