# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


def viz_id_to_pgm_id(id_str: str) -> int:
    """Convert a viz element ID string to a PGM ID integer."""
    for suffix in ["_0", "_1", "_2"]:
        id_str = id_str.replace(suffix, "")
    return int(id_str)
