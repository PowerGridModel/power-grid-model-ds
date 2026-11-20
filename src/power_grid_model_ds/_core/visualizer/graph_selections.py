# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Manage graph selections retained for comparison."""

from typing import TypedDict


class GraphSelection(TypedDict):
    """Identity of a selected component attribute."""

    group: str
    id: int
    column: str


def add_graph_selection(
    selections: list[GraphSelection],
    selection: GraphSelection,
) -> list[GraphSelection]:
    """Add a selection without duplicating an existing graph."""
    if selection in selections:
        return selections.copy()

    return [*selections, selection.copy()]


def remove_graph_selection(
    selections: list[GraphSelection],
    selection: GraphSelection,
) -> list[GraphSelection]:
    """Remove one selected graph while retaining the others."""
    return [item for item in selections if item != selection]


def clear_graph_selections() -> list[GraphSelection]:
    """Remove all retained graph selections."""
    return []
