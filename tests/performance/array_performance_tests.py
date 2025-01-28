# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Performace tests for the power_grid_model_ds package.

These are deliberately not prefixed with test_ so they are not run by pytest.
"""

# pylint: disable=missing-function-docstring

import logging

from tests.performance._constants import (
    ARRAY_SETUP_CODES,
    ARRAY_SIZES_LARGE,
    ARRAY_SIZES_SMALL,
    LOOP_REPEATS,
    SINGLE_REPEATS,
)
from tests.performance._helpers import do_performance_test

logging.basicConfig(level=logging.INFO)


def perftest_initialize():
    do_performance_test("pass", ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_slice():
    do_performance_test("input_array[0:10]", ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_set_attr():
    code_to_test = {
        "structured": "input_array['id'] = 1",
        "rec": "input_array.id = 1",
        "fancy": "input_array.id = 1",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_set_field():
    do_performance_test("input_array['id'] = 1", ARRAY_SIZES_LARGE, SINGLE_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_slice_1():
    code_to_test = "for i in range({size}): input_array[i]"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_data_slice_1():
    code_to_test = {
        "structured": "for i in range({size}): input_array[i]",
        "rec": "for i in range({size}): input_array[i]",
        "fancy": "for i in range({size}): input_array.data[i]",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_slice():
    code_to_test = "for i in range({size}): input_array[i:i+1]"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_set_field():
    code_to_test = "for i in range({size}): input_array['id'][i] = 1"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_get_field():
    code_to_test = "for row in input_array: row['id']"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_data_get_field():
    code_to_test = "for row in input_array.data: row['id']"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, LOOP_REPEATS, ARRAY_SETUP_CODES)


def perftest_loop_get_attr():
    code_to_test = "for row in input_array: row.id"
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, 100, ARRAY_SETUP_CODES)


def perftest_fancypy_concat():
    code_to_test = {
        "structured": "import numpy as np;np.concatenate([input_array, input_array])",
        "rec": "import numpy as np;np.concatenate([input_array, input_array])",
        "fancy": "import power_grid_model_ds.fancypy as fp;fp.concatenate(input_array, input_array)",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_LARGE, 100, ARRAY_SETUP_CODES)


def perftest_fancypy_unique():
    code_to_test = {
        "structured": "import numpy as np;np.unique(input_array)",
        "rec": "import numpy as np;np.unique(input_array)",
        "fancy": "import power_grid_model_ds.fancypy as fp;fp.unique(input_array)",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, 100, ARRAY_SETUP_CODES)


def perftest_fancypy_sort():
    code_to_test = {
        "structured": "import numpy as np;np.sort(input_array)",
        "rec": "import numpy as np;np.sort(input_array)",
        "fancy": "import power_grid_model_ds.fancypy as fp;fp.sort(input_array)",
    }
    do_performance_test(code_to_test, ARRAY_SIZES_SMALL, 100, ARRAY_SETUP_CODES)


if __name__ == "__main__":
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()

    perftest_initialize()
    perftest_slice()
    perftest_set_field()
    perftest_set_attr()

    perftest_loop_slice_1()
    perftest_loop_data_slice_1()
    perftest_loop_slice()
    perftest_loop_set_field()
    perftest_loop_get_field()
    perftest_loop_data_get_field()
    perftest_loop_get_attr()

    perftest_fancypy_concat()
    perftest_fancypy_unique()
    perftest_fancypy_sort()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats(20)
