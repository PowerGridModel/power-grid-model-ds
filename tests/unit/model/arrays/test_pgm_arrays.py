# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest
from numpy.testing import assert_array_equal

from power_grid_model_ds._core.model.arrays import BranchArray

# pylint: disable=missing-function-docstring


@pytest.fixture(name="branches")
def parallel_branches():
    branches = BranchArray.zeros(3)
    branches.from_node = [0, 0, 1]
    branches.to_node = [1, 1, 2]
    return branches


def test_branch_is_active():
    branches = BranchArray.zeros(4)
    branches.from_status = [1, 1, 0, 0]
    branches.to_status = [1, 0, 1, 0]

    assert_array_equal(branches.is_active, [True, False, False, False])
    assert branches[0].is_active


def test_branch_node_ids():
    branches = BranchArray.zeros(2)
    branches.from_node = [0, 1]
    branches.to_node = [1, 2]

    assert_array_equal(branches.node_ids, [0, 1, 1, 2])


def test_filter_non_parallel(branches: BranchArray):
    filtered_branches = branches.filter_parallel(1, "eq")
    assert_array_equal(filtered_branches.data, branches[2].data)


def test_filter_parallel(branches: BranchArray):
    filtered_branches = branches.filter_parallel(1, "neq")
    assert_array_equal(filtered_branches.data, branches[0:2].data)
