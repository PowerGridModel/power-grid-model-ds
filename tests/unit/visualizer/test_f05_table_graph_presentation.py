# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Regression tests for F05 table presentation and attribute traces."""

from types import SimpleNamespace

import numpy as np
import plotly.graph_objects as go
import pytest

from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    _add_attribute_traces,
    _to_data_table,
)


def test_output_columns_have_readable_headers_and_widths():
    array_data = SimpleNamespace(columns=["id", "u_rated"])
    rows = [
        {
            "id": 1,
            "u_rated": 400.0,
            "output__u": 401.0,
            "output__p": 100.0,
        }
    ]

    table = _to_data_table(array_data, "node", rows)
    columns = {column["field"]: column for column in table.columnDefs}

    assert columns["u_rated"]["headerName"] == "u_rated"
    assert columns["output__u"]["headerName"] == "Output: u"
    assert columns["output__p"]["headerName"] == "Output: p"
    assert columns["output__u"]["width"] >= 170
    assert columns["output__u"]["headerTooltip"] == "Output: u"
    assert table.dashGridOptions["suppressHorizontalScroll"] is False
    assert table.rowData == rows


def test_table_preserves_missing_output_values():
    array_data = SimpleNamespace(columns=["id"])
    rows = [{"id": 1, "output__u": None}]

    table = _to_data_table(array_data, "node", rows)

    assert table.rowData[0]["output__u"] is None


@pytest.mark.parametrize("series_count", [1, 2, 3, 4])
def test_multiseries_graph_accepts_different_series_counts(series_count):
    figure = go.Figure()
    x_values = np.arange(4)
    y_values = np.arange(4 * series_count).reshape(4, series_count)

    result = _add_attribute_traces(figure, x_values, y_values, "u")

    assert result is True
    assert len(figure.data) == series_count

    for index, trace in enumerate(figure.data):
        assert trace.name == f"u_phase_{index}"
        assert len(trace.x) == 4
        assert len(trace.y) == 4


def test_scalar_graph_creates_one_trace():
    figure = go.Figure()

    result = _add_attribute_traces(
        figure,
        np.array([0, 1, 2]),
        np.array([230.0, 231.0, 229.0]),
        "u",
    )

    assert result is True
    assert len(figure.data) == 1


@pytest.mark.parametrize(
    ("x_values", "y_values"),
    [
        (np.array([]), np.array([])),
        (np.array([0, 1]), np.array([230.0])),
        (np.array([0, 1]), np.ones((3, 2))),
        (np.array([0, 1]), np.empty((2, 0))),
        (np.array([0, 1]), np.ones((2, 2, 2))),
    ],
)
def test_invalid_graph_shapes_are_rejected(x_values, y_values):
    figure = go.Figure()

    result = _add_attribute_traces(figure, x_values, y_values, "u")

    assert result is False
    assert len(figure.data) == 0
