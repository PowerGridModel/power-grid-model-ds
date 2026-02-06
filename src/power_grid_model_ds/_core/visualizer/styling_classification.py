from enum import StrEnum
from typing import Literal

from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays.pgm_arrays import BranchArray, NodeArray


class StyleClass(StrEnum):
    """Styling classes used in the visualizer."""

    NODE = "node"
    SUBSTATION_NODE = "substation_node"
    LARGE_ID_NODE = "large_id_node"
    BRANCH = "branch"
    OPEN_BRANCH = "open_branch"
    OPEN_BRANCH_FROM = "open_branch_from"
    OPEN_BRANCH_TO = "open_branch_to"
    LINE = "line"
    TRANSFORMER = "transformer"
    LINK = "link"
    GENERIC_BRANCH = "generic_branch"
    ASYM_LINE = "asym_line"


def get_node_classification(node_arr: NodeArray) -> str:
    """Get the space separated string of styling classes for a node."""
    classes = [StyleClass.NODE]
    if node_arr.id > 10000000:
        classes.append(StyleClass.LARGE_ID_NODE)
    if node_arr.node_type == 1:
        classes.append(StyleClass.SUBSTATION_NODE)
    return " ".join((entry.value for entry in classes))


def get_branch_classification(
    branch_arr: BranchArray,
    component_type: Literal[
        ComponentType.transformer,
        ComponentType.three_winding_transformer,
        ComponentType.link,
        ComponentType.generic_branch,
        ComponentType.line,
        ComponentType.asym_line,
    ],
) -> str:
    """Get the space separated string of styling classes for a branch."""
    classes = [StyleClass.BRANCH]

    if component_type != ComponentType.line:
        type_to_vizclass = {
            ComponentType.transformer: StyleClass.TRANSFORMER,
            ComponentType.three_winding_transformer: StyleClass.TRANSFORMER,
            ComponentType.link: StyleClass.LINK,
            ComponentType.generic_branch: StyleClass.GENERIC_BRANCH,
            ComponentType.asym_line: StyleClass.ASYM_LINE,
        }
        classes.append(type_to_vizclass[component_type])

    if branch_arr.from_status == 0 or branch_arr.to_status == 0:
        classes.append(StyleClass.OPEN_BRANCH)
    if branch_arr.from_status == 0:
        classes.extend([StyleClass.OPEN_BRANCH_FROM])
    if branch_arr.to_status == 0:
        classes.extend([StyleClass.OPEN_BRANCH_TO])

    return " ".join((entry.value for entry in classes))
