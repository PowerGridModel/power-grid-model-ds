# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

import numpy as np
import pytest

from power_grid_model_ds._core.model.arrays.base import array as array_module
from power_grid_model_ds._core.model.arrays.base.array import (
    _parse_annotation_post_25,
    _parse_annotation_pre_25,
)


class TestParseAnnotationPre25:
    def test_scalar(self):
        type_args = (tuple[Any, ...], np.dtype[np.int64])
        assert _parse_annotation_pre_25("value", None, type_args, {}) == ("value", np.int64)

    def test_ndarray3(self):
        type_args = (np.ndarray[tuple[Any, ...], np.dtype[np.float64]], Literal[3])
        assert _parse_annotation_pre_25("value", None, type_args, {}) == ("value", np.float64, 3)

    def test_str_length_folding(self):
        type_args = (tuple[Any, ...], np.dtype[np.str_])
        assert _parse_annotation_pre_25("name", None, type_args, {"name": 100}) == ("name", np.dtype("U100"))

    def test_str_default_length(self):
        type_args = (tuple[Any, ...], np.dtype[np.str_])
        expected = ("name", np.dtype(f"U{array_module._DEFAULT_STR_LENGTH}"))
        assert _parse_annotation_pre_25("name", None, type_args, {}) == expected

    def test_unsupported_shape_raises(self):
        with pytest.raises(ValueError, match="not understood or supported"):
            _parse_annotation_pre_25("value", "bad", (), {})

    def test_malformed_ndarray3_raises(self):
        # A Literal-tagged annotation whose inner element lacks the expected nested structure must
        # raise the clear ValueError rather than an opaque IndexError.
        type_args = (int, Literal[3])
        with pytest.raises(ValueError, match="not understood or supported"):
            _parse_annotation_pre_25("value", "bad", type_args, {})


class TestParseAnnotationPost25:
    def test_scalar(self):
        assert _parse_annotation_post_25("value", None, (np.int64,), {}) == ("value", np.int64)

    def test_ndarray3(self):
        type_args = (np.dtype[np.float64], Literal[3])
        assert _parse_annotation_post_25("value", None, type_args, {}) == ("value", np.float64, 3)

    def test_str_length_folding(self):
        assert _parse_annotation_post_25("name", None, (np.str_,), {"name": 100}) == ("name", np.dtype("U100"))

    def test_str_default_length(self):
        expected = ("name", np.dtype(f"U{array_module._DEFAULT_STR_LENGTH}"))
        assert _parse_annotation_post_25("name", None, (np.str_,), {}) == expected

    def test_unsupported_shape_raises(self):
        with pytest.raises(ValueError, match="not understood or supported"):
            _parse_annotation_post_25("value", "bad", (), {})
