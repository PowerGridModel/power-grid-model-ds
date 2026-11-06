# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for rendering multiple retained graphs."""

from unittest.mock import patch

import plotly.graph_objects as go
from dash import dcc, html

from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    render_retained_graphs,
)

_CALLBACK_PATH = "power_grid_model_ds._core.visualizer.callbacks.element_selection.cell_selection_graph"

SENSOR_A = {
    "group": "sym_voltage_sensor",
    "id": 101,
    "column": "u_measured",
}

SENSOR_B = {
    "group": "sym_voltage_sensor",
    "id": 102,
    "column": "u_measured",
}


def _figure(values):
    figure = go.Figure()
    figure.add_scatter(
        x=[0, 1, 2],
        y=values,
    )
    return figure


def test_no_retained_selections_produces_no_graphs():
    assert render_retained_graphs([], 2.0) == []


def test_two_selections_produce_two_graph_cards():
    with patch(
        _CALLBACK_PATH,
        side_effect=[
            (_figure([230, 231, 232]), {"display": "block"}, {}),
            (_figure([235, 236, 237]), {"display": "block"}, {}),
        ],
    ) as renderer:
        cards = render_retained_graphs(
            [SENSOR_A, SENSOR_B],
            2.0,
        )

    assert len(cards) == 2
    assert all(isinstance(card, html.Div) for card in cards)

    assert cards[0].children[0].children[0].children == ("sym_voltage_sensor | ID 101 | u_measured")
    assert cards[1].children[0].children[0].children == ("sym_voltage_sensor | ID 102 | u_measured")

    assert isinstance(cards[0].children[2], dcc.Graph)
    assert isinstance(cards[1].children[2], dcc.Graph)

    assert renderer.call_count == 2


def test_retained_graphs_use_current_sigma_multiplier():
    with patch(
        _CALLBACK_PATH,
        return_value=(
            _figure([230, 231, 232]),
            {"display": "block"},
            {},
        ),
    ) as renderer:
        render_retained_graphs([SENSOR_A], 3.0)

    renderer.assert_called_once_with(SENSOR_A, 3.0)


def test_unavailable_graph_displays_message():
    with patch(
        _CALLBACK_PATH,
        return_value=(
            go.Figure(),
            {"display": "none"},
            {"display": "none"},
        ),
    ):
        cards = render_retained_graphs(
            [SENSOR_A],
            2.0,
        )

    assert len(cards) == 1
    assert isinstance(cards[0].children[2], html.P)
    assert "unavailable" in cards[0].children[2].children


def test_invalid_selection_is_skipped():
    cards = render_retained_graphs(
        [{"group": "sym_voltage_sensor", "id": "invalid"}],
        2.0,
    )

    assert cards == []


def test_each_graph_has_its_own_remove_button():
    with patch(
        _CALLBACK_PATH,
        return_value=(
            _figure([230, 231, 232]),
            {"display": "block"},
            {},
        ),
    ):
        cards = render_retained_graphs(
            [SENSOR_A, SENSOR_B],
            2.0,
        )

    first_button = cards[0].children[0].children[1]
    second_button = cards[1].children[0].children[1]

    assert first_button.id == {
        "type": "remove-retained-graph",
        "index": 0,
    }
    assert second_button.id == {
        "type": "remove-retained-graph",
        "index": 1,
    }

    assert first_button.children[1] == "Remove"
    assert second_button.children[1] == "Remove"

    assert first_button.children[0].className == "fa-solid fa-xmark"
    assert second_button.children[0].className == "fa-solid fa-xmark"
