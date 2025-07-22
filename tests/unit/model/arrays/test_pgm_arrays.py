# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest
from numpy.testing import assert_array_equal

from power_grid_model_ds._core.model.arrays import Branch3Array, BranchArray

# pylint: disable=missing-function-docstring


@pytest.fixture(name="branches")
def parallel_branches():
    branches = BranchArray.zeros(3)
    branches.from_node = [0, 0, 1]
    branches.to_node = [1, 1, 2]
    return branches


class TestBranchArray:
    def test_branch_is_active(self):
        branches = BranchArray.zeros(4)
        branches.from_status = [1, 1, 0, 0]
        branches.to_status = [1, 0, 1, 0]

        assert_array_equal(branches.is_active, [True, False, False, False])
        assert branches[0].is_active

    def test_branch_node_ids(self):
        branches = BranchArray.zeros(2)
        branches.from_node = [0, 1]
        branches.to_node = [1, 2]

        assert_array_equal(branches.node_ids, [0, 1, 1, 2])

    def test_filter_non_parallel(self, branches: BranchArray):
        filtered_branches = branches.filter_parallel(1, "eq")
        assert_array_equal(filtered_branches.data, branches[2].data)

    def test_filter_parallel(self, branches: BranchArray):
        filtered_branches = branches.filter_parallel(1, "neq")
        assert_array_equal(filtered_branches.data, branches[0:2].data)


class TestBranch3Array:
    def test_as_branches_single(self):
        branch3 = Branch3Array(
            node_1=[1],
            node_2=[2],
            node_3=[3],
            status_1=[1],
            status_2=[1],
            status_3=[0],
        )

        branch_array = branch3.as_branches()

        assert branch_array.size == 3

        assert branch_array.from_node.tolist() == [1, 1, 2]
        assert branch_array.to_node.tolist() == [2, 3, 3]
        assert branch_array.from_status.tolist() == [1, 1, 1]
        assert branch_array.to_status.tolist() == [1, 0, 0]

    def test_as_branches_multiple(self):
        branch3 = Branch3Array(
            node_1=[1, 4],
            node_2=[2, 5],
            node_3=[3, 6],
            status_1=[1, 1],
            status_2=[1, 1],
            status_3=[1, 0],
        )

        branch_array = branch3.as_branches()
        branch_array.sort(order=["from_node", "to_node"])

        assert branch_array.size == 6
        assert branch_array.from_node.tolist() == [1, 1, 2, 4, 4, 5]
        assert branch_array.to_node.tolist() == [2, 3, 3, 5, 6, 6]
        assert branch_array.from_status.tolist() == [1, 1, 1, 1, 1, 1]
        assert branch_array.to_status.tolist() == [1, 1, 1, 1, 0, 0]
