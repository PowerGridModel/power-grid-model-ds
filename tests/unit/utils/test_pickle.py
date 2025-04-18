# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from pathlib import Path
from unittest.mock import patch

import pytest

from power_grid_model_ds._core.utils import pickle as pickle_mod
from power_grid_model_ds._core.utils.pickle import get_pickle_path

# pylint: disable=missing-function-docstring


@pytest.fixture(name="pickle_path")
def fixture_pickle_path():
    pickle_path = Path("my_file.pickle")
    pickle_path.touch()
    yield pickle_path
    pickle_path.unlink()


@pytest.fixture(name="gzip_path")
def fixture_gzip_path():
    pickle_path = Path("my_file.pickle.gz")
    pickle_path.touch()
    yield pickle_path
    pickle_path.unlink()


def test_get_pickle_path(pickle_path: Path):
    found_pickle_path = get_pickle_path(pickle_path)
    assert pickle_path == found_pickle_path


def test_get_pickle_path_gz(gzip_path: Path):
    with patch.object(pickle_mod, "gzip2file") as mock:
        get_pickle_path(gzip_path)
    assert 1 == mock.call_count


def test_get_pickle_path_find_gz(gzip_path: Path):
    """Test that .pickle.gz can be automagically found."""
    pickle_path = gzip_path.with_suffix("")
    with patch.object(pickle_mod, "gzip2file") as mock:
        get_pickle_path(pickle_path)
    assert 1 == mock.call_count
