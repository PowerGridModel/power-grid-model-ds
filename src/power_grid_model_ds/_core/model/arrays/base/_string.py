# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Module for array to string conversion."""

from typing import TYPE_CHECKING, Optional

import numpy as np

from power_grid_model_ds._core import fancypy as fp

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.arrays.base.array import FancyArray


def convert_array_to_string(array: "FancyArray", rows: int = 10, column_width: int | str = "auto") -> str:
    """Return a string representation of the array as a table.

    Args:
        column_width: the width of each column in the table. Will be determined by its contents if set to "auto".
        rows: the number of rows to show. If the array is larger than this, the middle rows are hidden.
    """
    start_rows, end_rows = _get_start_and_end_rows(array, rows)
    if end_rows is not None:
        rows_to_print = fp.concatenate(start_rows, end_rows)
    else:
        rows_to_print = start_rows

    match column_width:
        case "auto":
            column_widths = _determine_column_widths(rows_to_print)
        case int():
            column_widths = [(column, column_width) for column in array.dtype.names]
        case _:
            raise NotImplementedError(f"column_width={column_width} is not supported. Use 'auto' or int.")

    header = "|".join(f"{_center_and_truncate(column, width)}" for column, width in column_widths) + "\n"
    if end_rows is None:
        body = _rows_to_strings(rows_to_print, column_widths)
        return header + "\n".join(body)

    start_rows = _rows_to_strings(start_rows, column_widths)
    cutoff_line = f"(..{array.size - rows_to_print.size} hidden rows..)".center(len(header))
    end_rows = _rows_to_strings(end_rows, column_widths)
    return header + "\n".join(start_rows) + "\n" + cutoff_line + "\n" + "\n".join(end_rows)


def _rows_to_strings(rows: "FancyArray", column_widths: list[tuple[str, int]]) -> list[str]:
    rows_as_strings = []
    for row in rows.data:
        row_as_strings = []
        for attr, (_, width) in zip(row.tolist(), column_widths):
            row_as_strings.append(_center_and_truncate(str(attr), width))
        rows_as_strings.append("|".join(row_as_strings))
    return rows_as_strings


def _determine_column_widths(array: "FancyArray") -> list[tuple[str, int]]:
    """Get the maximum width of each column in the array."""
    column_widths: list[tuple[str, int]] = []
    if not array.dtype.names:
        return column_widths

    for column in array.dtype.names:
        data = array.data[column]
        if data.size:
            # if float, round to 3 decimals
            if data.dtype.kind == "f":
                data = np.around(data, decimals=3)
            # to string to get the length
            data = data.astype(str)
            longest_string = max(data, key=len)
            if len(column) > len(longest_string):
                longest_string = column
        else:
            longest_string = column
        column_widths.append((column, len(longest_string) + 2))
    return column_widths


def _center_and_truncate(string: str, width: int) -> str:
    if len(string) <= width:
        return string.center(width)
    return f"{string[: width - 2]}..".center(width)


def _get_start_and_end_rows(array: "FancyArray", rows: int) -> tuple["FancyArray", Optional["FancyArray"]]:
    if array.size <= rows:
        return array, None
    cutoff = rows // 2
    start_rows = array[:cutoff]
    end_rows = array[-cutoff:]
    return start_rows, end_rows
