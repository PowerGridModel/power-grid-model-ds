# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import inspect
import timeit
from itertools import product
from typing import Generator, Union


def do_performance_test(
    code_to_test: Union[str, dict[str, str], list[str]],
    size_list: list[int],
    repeats: int,
    setup_codes: dict[str, str],
):
    """Generalized performance test runner."""
    print(f"{'-' * 20} {inspect.stack()[1][3]} {'-' * 20}")

    for size in size_list:
        formatted_setup_codes = {key: code.format(size=size) for key, code in setup_codes.items()}
        if isinstance(code_to_test, dict):
            code_to_test_list = [code_to_test[variant].format(size=size) for variant in setup_codes]
            test_generator = zip(formatted_setup_codes.items(), code_to_test_list)
        elif isinstance(code_to_test, list):
            code_to_test_list = [code.format(size=size) for code in code_to_test]
            test_generator = product(formatted_setup_codes.items(), code_to_test_list)
        else:
            test_generator = product(formatted_setup_codes.items(), [code_to_test.format(size=size)])

        print(f"\n\tsize: {size}\n")

        timings = _get_timings(test_generator, repeats=repeats)
        _print_timings(timings)

    print()


def _print_timings(timings: Generator):
    for key, code, timing in timings:
        code = code.split(";")[-1].replace("\n", " ").replace("\t", " ")
        code = f"{key}: {code}"

        if isinstance(timing, Exception):
            print(f"\t\t{code.ljust(100)} | Not supported")
            continue
        print(f"\t\t{code.ljust(100)} | {sum(timing):.2f}s")


def _get_timings(test_generator, repeats: int):
    """Return a generator with the timings for each array type."""
    for (key, setup_code), test_code in test_generator:
        if test_code == "pass":
            yield key, "intialise", timeit.repeat(setup_code, number=repeats)
        else:
            try:
                yield key, test_code, timeit.repeat(test_code, setup_code, number=repeats)
            # pylint: disable=broad-exception-caught
            except Exception as error:  # noqa
                yield key, test_code, error
