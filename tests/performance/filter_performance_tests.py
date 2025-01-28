# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from tests.performance._constants import ARRAY_SETUP_CODES, ARRAY_SIZES_LARGE, SINGLE_REPEATS
from tests.performance._helpers import do_performance_test

# pylint: disable=missing-function-docstring


def perftest_get():
    code_to_test = {
        "structured": "input_array[np.isin(input_array['id'], 99)]",
        "rec": "input_array[np.isin(input_array['id'], 99)]",
        "fancy": "try:\n\tinput_array.get(id=99)\nexcept:\n\tpass",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_filter():
    code_to_test = {
        "structured": "input_array[np.isin(input_array['id'], 99)]",
        "rec": "input_array[np.isin(input_array['id'], 99)]",
        "fancy": "input_array.filter(id=99)",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_update_by_id():
    code_to_test = {
        "structured": "input_array['test_float'][np.isin(input_array['id'], np.arange({size}))] = 42.0",
        "rec": "input_array['test_float'][np.isin(input_array['id'], np.arange({size}))] = 42.0",
        "fancy": "input_array.update_by_id(ids=np.arange({size}), test_float=42.0, allow_missing = False)",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


if __name__ == "__main__":
    perftest_get()
    perftest_filter()
    perftest_update_by_id()
