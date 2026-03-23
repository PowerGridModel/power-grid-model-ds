# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from pathlib import Path

# noinspection PyPackageRequirements
from setuptools import setup


def set_version(pkg_dir: Path):
    # if PYPI_VERSION does not exist, copy from VERSION
    pypi_file = pkg_dir / "PYPI_VERSION"
    if not pypi_file.exists():
        with Path(pkg_dir / "VERSION").open() as f:
            version = f.read().strip().strip("\n")
        with Path(pypi_file).open("w") as f:
            f.write(version)


def prepare_pkg(setup_file: Path):
    """

    Args:
        setup_file:
    Returns:

    """
    pkg_dir = setup_file.parent
    set_version(pkg_dir)


prepare_pkg(Path(__file__).resolve())
setup()
