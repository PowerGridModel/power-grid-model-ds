# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for IdTracker."""

from power_grid_model_ds._core.model.containers._id_tracker import IdTracker


def test_empty_init():
    tracker = IdTracker()
    assert tracker.ids == set()
    assert tracker.max_id == 0


def test_init_from_set():
    tracker = IdTracker({1, 5, 3})
    assert tracker.ids == {1, 3, 5}
    assert tracker.max_id == 5


def test_init_copies_input_set():
    ids = {1, 2, 3}
    tracker = IdTracker(ids)
    ids.add(99)
    assert tracker.ids == {1, 2, 3}
    assert tracker.max_id == 3


def test_add_higher_ids():
    tracker = IdTracker({1, 2})
    tracker.add({5, 7})
    assert tracker.ids == {1, 2, 5, 7}
    assert tracker.max_id == 7


def test_add_lower_ids():
    tracker = IdTracker({10, 20})
    tracker.add({3, 4})
    assert tracker.ids == {3, 4, 10, 20}
    assert tracker.max_id == 20


def test_add_empty_set():
    tracker = IdTracker({1, 2})
    tracker.add(set())
    assert tracker.ids == {1, 2}
    assert tracker.max_id == 2


def test_add_with_max_new_id():
    tracker = IdTracker({1})
    tracker.add({2, 3}, max_new_id=100)
    assert tracker.ids == {1, 2, 3}
    assert tracker.max_id == 100
