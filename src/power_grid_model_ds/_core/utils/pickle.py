# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""helper functions for pickling python objects and loading pickle objects"""

import pickle
from pathlib import Path

from power_grid_model_ds._core.utils.zip import gzip2file


def save_to_pickle(path: Path, python_object: object):
    """Save a python object to pickle"""
    path.parent.mkdir(exist_ok=True, parents=True)
    with Path(str(path)).open("wb") as file:
        pickle.dump(python_object, file)


def load_from_pickle(path: Path) -> object:
    """Load a python object from a pickle file"""
    with path.open("rb") as file:
        return pickle.load(file)  # noqa S301


def get_pickle_path(path: Path) -> Path:
    """
    Returns the path to the pickle file.
    If ony a .gz-file is available, the .gz-file is unpacked.
    """
    pickle_suffix = ".pickle"
    gz_suffix = ".gz"

    if path.suffix == pickle_suffix and path.is_file():
        return path

    if path.with_suffix(pickle_suffix).is_file():
        return path.with_suffix(pickle_suffix)

    if path.suffix == gz_suffix and path.is_file():
        return gzip2file(path)

    pickle_gz_suffix = pickle_suffix + gz_suffix
    if path.with_suffix(pickle_gz_suffix).is_file():
        return gzip2file(path.with_suffix(pickle_gz_suffix))

    raise FileNotFoundError(f"Expected either {path.name}.pickle or {path.name}.pickle.gz")
