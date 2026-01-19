# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


class JSONSerializationError(Exception):
    """Exception raised for errors during JSON serialization of grid attributes."""


class JSONDeserializationError(Exception):
    """Exception raised for errors during JSON deserialization of grid attributes."""
