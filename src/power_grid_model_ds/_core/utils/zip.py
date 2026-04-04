# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper functions for (un)zipping files"""

import gzip
import logging
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

_logger = logging.getLogger(__name__)


def zip_folder(folder_to_zip: Path) -> Path:
    """Zip folder contents"""
    zip_file_path = folder_to_zip.with_suffix(".zip").resolve()
    folder_to_zip = folder_to_zip.resolve()

    # move into folder to zip to avoid nested folders in .zip file
    current_working_directory = Path.cwd()
    os.chdir(folder_to_zip)
    files_to_zip = [path.relative_to(folder_to_zip) for path in folder_to_zip.rglob("*")]
    zip_files(zip_file_path, files_to_zip)

    # move out of folder again
    os.chdir(current_working_directory)

    return zip_file_path


def zip_files(zip_file_path: Path, files_to_zip: list[Path]) -> Path:
    """Zip files"""
    with ZipFile(str(zip_file_path.with_suffix(".zip")), "w") as zip_object:
        for file in files_to_zip:
            zip_object.write(str(file))
        zip_object.close()
    return zip_file_path.resolve()


def unzip_files(zip_file_path: Path) -> Path:
    """Unzip .zip file to folder"""
    extraction_dir = zip_file_path.with_suffix("")
    extraction_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(str(zip_file_path.resolve()), "r") as zip_ref:
        zip_ref.extractall(extraction_dir)
    return extraction_dir


def gzip2file(gzip_path: Path) -> Path:
    """unzip a gzip (.gz) file"""
    _logger.info("Unzipping %s", gzip_path.name)

    file_path = gzip_path.with_suffix("")
    with gzip.open(gzip_path, "rb") as f_in, Path(file_path).open("wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return file_path


def file2gzip(file_path: Path) -> Path:
    """zip a gzip (.gz) file"""
    _logger.info("Zipping %s", file_path.name)

    gzip_path = file_path.with_suffix(f"{file_path.suffix}.gz")
    with Path(file_path).open("rb") as f_in, gzip.open(gzip_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return gzip_path
