# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tracks a set of ids and its maximum value."""


class IdTracker:
    """Wrapper around a set of ids that keeps track of the maximum id."""

    __hash__ = None

    def __init__(self, ids: set[int] | None = None) -> None:
        """Initialize the tracker with an optional set of ids."""
        self._ids = set(ids) if ids is not None else set()
        self._max_id = max(self._ids) if self._ids else 0

    @property
    def ids(self) -> set[int]:
        """Return the tracked ids."""
        return self._ids

    @property
    def max_id(self) -> int:
        """Return the cached maximum id."""
        return self._max_id

    def add(self, new_ids: set[int], max_new_id: int | None = None) -> None:
        """Add ids and update the cached maximum id."""
        self._ids |= new_ids
        if max_new_id is not None:
            self._max_id = max(self._max_id, max_new_id)
        elif new_ids:
            self._max_id = max(self._max_id, *new_ids)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._ids == other._ids and self._max_id == other._max_id
