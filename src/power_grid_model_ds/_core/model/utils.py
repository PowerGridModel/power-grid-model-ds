# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from power_grid_model_ds._core.model.arrays.pgm_arrays import Branch3Array, BranchArray


def _get_branch3_branches(branch3: Branch3Array) -> BranchArray:
    node_1 = branch3.node_1.item()
    node_2 = branch3.node_2.item()
    node_3 = branch3.node_3.item()

    status_1 = branch3.status_1.item()
    status_2 = branch3.status_2.item()
    status_3 = branch3.status_3.item()

    branches = BranchArray.zeros(3)
    branches.from_node = [node_1, node_1, node_2]
    branches.to_node = [node_2, node_3, node_3]
    branches.from_status = [status_1, status_1, status_2]
    branches.to_status = [status_2, status_3, status_3]

    return branches
