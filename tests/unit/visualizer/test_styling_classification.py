# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays import LineArray, NodeArray
from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymLineArray,
    GenericBranchArray,
    LinkArray,
    TransformerArray,
)
from power_grid_model_ds._core.visualizer.styling_classification import (
    StyleClass,
    get_branch_classification,
    get_node_classification,
)


class TestGetNodeClassification:
    """Test get_node_classification function."""

    @pytest.mark.parametrize(
        ("node_id", "node_type", "expected_classes"),
        [
            pytest.param(100, 0, [StyleClass.NODE], id="basic_node"),
            pytest.param(10000001, 0, [StyleClass.NODE, StyleClass.LARGE_ID_NODE], id="large_id_node"),
            pytest.param(100, 1, [StyleClass.NODE, StyleClass.SUBSTATION_NODE], id="substation_node"),
            pytest.param(
                20000000,
                1,
                [StyleClass.NODE, StyleClass.LARGE_ID_NODE, StyleClass.SUBSTATION_NODE],
                id="large_id_substation_node",
            ),
            pytest.param(10000000, 0, [StyleClass.NODE], id="boundary_id_not_large"),
        ],
    )
    def test_node_classification(self, node_id, node_type, expected_classes):
        """Test classification for various node configurations."""
        node = NodeArray.zeros(1)
        node["id"] = node_id
        node["node_type"] = node_type

        result = get_node_classification(node)
        expected = " ".join(cls.value for cls in expected_classes)
        assert result == expected

        # Verify all expected classes are present
        for cls in expected_classes:
            assert cls.value in result


class TestGetBranchClassification:
    """Test get_branch_classification function."""

    @pytest.mark.parametrize(
        ("array_type", "component_type", "from_status", "to_status", "expected_classes"),
        [
            pytest.param(LineArray, ComponentType.line, 1, 1, [StyleClass.BRANCH], id="line_closed"),
            pytest.param(
                LineArray,
                ComponentType.line,
                0,
                1,
                [StyleClass.BRANCH, StyleClass.OPEN_BRANCH, StyleClass.OPEN_BRANCH_FROM],
                id="line_open_from",
            ),
            pytest.param(
                LineArray,
                ComponentType.line,
                1,
                0,
                [StyleClass.BRANCH, StyleClass.OPEN_BRANCH, StyleClass.OPEN_BRANCH_TO],
                id="line_open_to",
            ),
            pytest.param(
                LineArray,
                ComponentType.line,
                0,
                0,
                [
                    StyleClass.BRANCH,
                    StyleClass.OPEN_BRANCH,
                    StyleClass.OPEN_BRANCH_FROM,
                    StyleClass.OPEN_BRANCH_TO,
                ],
                id="line_open_both",
            ),
            pytest.param(
                TransformerArray,
                ComponentType.transformer,
                1,
                1,
                [StyleClass.BRANCH, StyleClass.TRANSFORMER],
                id="transformer_closed",
            ),
            pytest.param(
                TransformerArray,
                ComponentType.transformer,
                0,
                1,
                [StyleClass.BRANCH, StyleClass.TRANSFORMER, StyleClass.OPEN_BRANCH, StyleClass.OPEN_BRANCH_FROM],
                id="transformer_open_from",
            ),
            pytest.param(
                TransformerArray,
                ComponentType.three_winding_transformer,
                1,
                1,
                [StyleClass.BRANCH, StyleClass.TRANSFORMER],
                id="three_winding_transformer",
            ),
            pytest.param(LinkArray, ComponentType.link, 1, 1, [StyleClass.BRANCH, StyleClass.LINK], id="link_closed"),
            pytest.param(
                LinkArray,
                ComponentType.link,
                0,
                0,
                [
                    StyleClass.BRANCH,
                    StyleClass.LINK,
                    StyleClass.OPEN_BRANCH,
                    StyleClass.OPEN_BRANCH_FROM,
                    StyleClass.OPEN_BRANCH_TO,
                ],
                id="link_open_both",
            ),
            pytest.param(
                GenericBranchArray,
                ComponentType.generic_branch,
                1,
                1,
                [StyleClass.BRANCH, StyleClass.GENERIC_BRANCH],
                id="generic_branch",
            ),
            pytest.param(
                AsymLineArray,
                ComponentType.asym_line,
                1,
                1,
                [StyleClass.BRANCH, StyleClass.ASYM_LINE],
                id="asym_line_closed",
            ),
            pytest.param(
                AsymLineArray,
                ComponentType.asym_line,
                1,
                0,
                [StyleClass.BRANCH, StyleClass.ASYM_LINE, StyleClass.OPEN_BRANCH, StyleClass.OPEN_BRANCH_TO],
                id="asym_line_open_to",
            ),
        ],
    )
    def test_branch_classification(self, array_type, component_type, from_status, to_status, expected_classes):
        """Test classification for various branch types and status combinations."""
        branch = array_type.zeros(1)
        branch["id"] = 100
        branch["from_node"] = 1
        branch["to_node"] = 2
        branch["from_status"] = from_status
        branch["to_status"] = to_status

        result = get_branch_classification(branch, component_type)
        expected = " ".join(cls.value for cls in expected_classes)
        assert result == expected

        # Verify all expected classes are present
        for cls in expected_classes:
            assert cls.value in result


class TestStyleClass:
    """Test StyleClass enum values."""

    @pytest.mark.parametrize(
        ("style_class", "expected_value"),
        [
            pytest.param(StyleClass.NODE, "node", id="node"),
            pytest.param(StyleClass.SUBSTATION_NODE, "substation_node", id="substation_node"),
            pytest.param(StyleClass.LARGE_ID_NODE, "large_id_node", id="large_id_node"),
            pytest.param(StyleClass.BRANCH, "branch", id="branch"),
            pytest.param(StyleClass.OPEN_BRANCH, "open_branch", id="open_branch"),
            pytest.param(StyleClass.OPEN_BRANCH_FROM, "open_branch_from", id="open_branch_from"),
            pytest.param(StyleClass.OPEN_BRANCH_TO, "open_branch_to", id="open_branch_to"),
            pytest.param(StyleClass.LINE, "line", id="line"),
            pytest.param(StyleClass.TRANSFORMER, "transformer", id="transformer"),
            pytest.param(StyleClass.LINK, "link", id="link"),
            pytest.param(StyleClass.GENERIC_BRANCH, "generic_branch", id="generic_branch"),
            pytest.param(StyleClass.ASYM_LINE, "asym_line", id="asym_line"),
        ],
    )
    def test_style_class_values(self, style_class, expected_value):
        """Test that StyleClass enum has expected values."""
        assert style_class.value == expected_value

    def test_style_class_is_string_enum(self):
        """Test that StyleClass is a StrEnum."""
        from enum import StrEnum

        assert issubclass(StyleClass, StrEnum)
