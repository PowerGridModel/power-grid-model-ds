# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Create a grid from text a text file"""

import logging
from typing import TYPE_CHECKING

from power_grid_model_ds._core.model.enums.nodes import NodeType

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid

_logger = logging.getLogger(__name__)


class TextSource:
    """Class for handling text sources.

    Text sources are only intended for test purposes so that a grid can quickly be designed from a text file.
    Moreover, these text sources are compatible with the grid editor at https://csacademy.com/app/graph_editor/

    Example of a text file:
        S1 2
        2 3
        3 4 transformer
        4 5
        S1 7

    See docs/examples/3_drawing_a_grid.md for more information.
    """

    def __init__(self, grid_class: type["Grid"]):
        self.grid = grid_class.empty()

    def load_from_txt(self, *args: str) -> "Grid":
        """Load a grid from text"""

        text_lines = [line for arg in args for line in arg.strip().split("\n")]

        txt_nodes, txt_branches = self.read_txt(text_lines)
        self.add_nodes(txt_nodes)
        self.add_branches(txt_branches)
        self.grid.set_feeder_ids()
        return self.grid

    @staticmethod
    def read_txt(txt_lines: list[str]) -> tuple[set, dict]:
        """Extract assets from text"""

        txt_nodes = set()
        txt_branches = {}
        for text_line in txt_lines:
            if not text_line.strip() or text_line.startswith("#"):
                continue  # skip empty lines and comments
            try:
                from_node_str, to_node_str, *comments = text_line.strip().split()
            except ValueError as err:
                raise ValueError(f"Text line '{text_line}' is invalid. Skipping...") from err
            comments = comments[0].split(",") if comments else []

            txt_nodes |= {from_node_str, to_node_str}
            txt_branches[(from_node_str, to_node_str)] = comments
        return txt_nodes, txt_branches

    def add_nodes(self, nodes: set[str]):
        """Add nodes to the grid"""
        source_nodes = {int(node[1:]) for node in nodes if node.startswith("S")}
        regular_nodes = {int(node) for node in nodes if not node.startswith("S")}

        if source_nodes.intersection(regular_nodes):
            raise ValueError("Source nodes and regular nodes have overlapping ids")

        for node_id in source_nodes:
            new_node = self.grid.node.empty(1)
            new_node.id = node_id
            new_node.node_type = NodeType.SUBSTATION_NODE
            self.grid.append(new_node, check_max_id=False)

        for node_id in regular_nodes:
            new_node = self.grid.node.empty(1)
            new_node.id = node_id
            self.grid.append(new_node, check_max_id=False)

    def add_branches(self, branches: dict[tuple[str, str], list[str]]):
        """Add branches to the grid"""
        for branch, comments in branches.items():
            self.add_branch(branch, comments)

    def add_branch(self, branch: tuple[str, str], comments: list[str]):
        """Add a branch to the grid"""
        from_node_str, to_node_str = branch
        from_node = int(from_node_str.replace("S", ""))
        to_node = int(to_node_str.replace("S", ""))

        if "transformer" in comments:
            new_branch = self.grid.transformer.empty(1)
        elif "link" in comments:
            new_branch = self.grid.link.empty(1)
        else:  # assume it is a line
            new_branch = self.grid.line.empty(1)

        branch_ids = [branch_id for branch_id in comments if branch_id.isdigit()]
        if branch_ids:
            if len(branch_ids) > 1:
                raise ValueError(f"Multiple branch ids found in row {branch} {','.join(comments)}")
            new_branch.id = int(branch_ids[0])

        new_branch.from_node = from_node
        new_branch.to_node = to_node
        new_branch.from_status = 1
        if "open" in comments:
            new_branch.to_status = 0
        else:
            new_branch.to_status = 1
        self.grid.append(new_branch, check_max_id=False)
