# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Comprehensive unit tests for Grid serialization with power-grid-model compatibility."""

from dataclasses import dataclass, fields
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.utils.serialization import (
    load_grid_from_json,
    save_grid_to_json,
)
from power_grid_model_ds.arrays import LineArray
from power_grid_model_ds.arrays import NodeArray as BaseNodeArray
from power_grid_model_ds.fancypy import array_equal


class ExtendedNodeArray(BaseNodeArray):
    """Test array with extended columns"""

    _defaults = {"u": 0.0, "analysis_flag": 0}
    u: NDArray[np.float64]
    analysis_flag: NDArray[np.int32]


class ExtendedLineArray(LineArray):
    """Test array with extended columns"""

    _defaults = {"i_from": 0.0, "loading_factor": 0.0}
    i_from: NDArray[np.float64]
    loading_factor: NDArray[np.float64]


@dataclass
class ExtendedGrid(Grid):
    """Test grid with extended arrays"""

    node: ExtendedNodeArray
    line: ExtendedLineArray

    value_extension: float = 0.0
    str_extension: str = "default"


@pytest.fixture
def basic_grid():
    """Basic grid fixture"""
    return Grid.from_txt("1 2", "2 3", "S10 1")


@pytest.fixture
def extended_grid():
    """Extended grid fixture with additional columns"""
    grid = ExtendedGrid.empty()
    grid.value_extension = 1.0
    grid.str_extension = "not_default"
    nodes = ExtendedNodeArray(
        id=[1, 2, 3], u_rated=[10500, 10500, 10500], u=[10450, 10400, 10350], analysis_flag=[1, 0, 1]
    )
    lines = ExtendedLineArray(
        id=[10, 11],
        from_node=[1, 2],
        to_node=[2, 3],
        from_status=[1, 1],
        to_status=[1, 1],
        r1=[0.1, 0.15],
        x1=[0.2, 0.25],
        c1=[1e-6, 1.2e-6],
        tan1=[0.0, 0.0],
        i_n=[400, 350],
        i_from=[150.5, 120.3],
        loading_factor=[0.75, 0.68],
    )
    grid.append(nodes)
    grid.append(lines)
    return grid


class TestSerializationRoundtrips:
    """Test serialization across different formats and configurations"""

    @pytest.mark.parametrize("grid_fixture", ("basic_grid", "extended_grid", "grid"))
    def test_serialization_roundtrip(self, request, grid_fixture, tmp_path: Path):
        """Test serialization roundtrip

        Scenarios:
        - Basic grid
        - Extended grid with extended arrays and additional non-array attributes
        - Empty grid
        """
        path = tmp_path / "extended.json"
        grid = request.getfixturevalue(grid_fixture)

        save_grid_to_json(grid, path)
        loaded_grid = load_grid_from_json(path, target_grid_class=grid.__class__)

        for field in fields(grid):
            if field.name in ["graphs"]:
                continue

            orig_value = getattr(grid, field.name)
            loaded_value = getattr(loaded_grid, field.name)

            if isinstance(loaded_value, FancyArray):
                assert array_equal(orig_value, loaded_value)
            else:
                assert orig_value == loaded_value


class TestCrossTypeCompatibility:
    """Test cross-type loading and compatibility"""

    def test_basic_to_extended_loading(self, basic_grid: Grid, tmp_path: Path):
        """Test loading basic grid into extended type"""
        path = tmp_path / "basic.json"

        # Save basic grid
        save_grid_to_json(basic_grid, path)
        loaded_grid = load_grid_from_json(path, target_grid_class=ExtendedGrid)

        # Core data should transfer
        array_equal(loaded_grid.node, basic_grid.node)
        array_equal(loaded_grid.line, basic_grid.line)

    def test_extended_to_basic_loading(self, extended_grid: ExtendedGrid, tmp_path: Path):
        """Test loading extended grid into basic type"""
        path = tmp_path / "extended.json"

        # Save extended grid
        save_grid_to_json(extended_grid, path)
        loaded_grid = load_grid_from_json(path, target_grid_class=Grid)

        # Core data should transfer
        array_equal(loaded_grid.node, extended_grid.node)
        array_equal(loaded_grid.line, extended_grid.line)


class TestExtensionHandling:
    """Test extension data handling and edge cases"""

    def test_custom_array_serialization_roundtrip(self, tmp_path: Path):
        """Test serialization and loading of grids with custom arrays"""

        # Create a custom array type that properly extends FancyArray
        class CustomMetadataArray(FancyArray):
            """Custom metadata array for testing"""

            _defaults = {"metadata_value": 0.0, "category": 0}

            id: NDArray[np.int32]
            metadata_value: NDArray[np.float64]
            category: NDArray[np.int32]

        # Create a grid with custom arrays
        @dataclass
        class GridWithCustomArray(Grid):
            custom_metadata: CustomMetadataArray

        # Create test grid with custom data
        grid = GridWithCustomArray.empty()

        # Add some basic grid data
        nodes = grid.node.__class__(id=[1, 2], u_rated=[10000, 10000])
        grid.append(nodes)

        # Add custom metadata
        custom_data = CustomMetadataArray(id=[100, 200, 300], metadata_value=[1.5, 2.5, 3.5], category=[1, 2, 1])
        grid.custom_metadata = custom_data

        # Test JSON serialization
        json_path = tmp_path / "custom_array.json"
        save_grid_to_json(grid, json_path)

        # Load back and verify
        loaded_grid = load_grid_from_json(json_path, target_grid_class=GridWithCustomArray)

        # Verify core data
        assert loaded_grid.node.size == 2
        np.testing.assert_array_equal(loaded_grid.node.id, [1, 2])

        # Verify custom array was preserved
        assert hasattr(loaded_grid, "custom_metadata")
        assert loaded_grid.custom_metadata.size == 3
        np.testing.assert_array_equal(loaded_grid.custom_metadata.id, [100, 200, 300])
        np.testing.assert_array_almost_equal(loaded_grid.custom_metadata.metadata_value, [1.5, 2.5, 3.5])
        np.testing.assert_array_equal(loaded_grid.custom_metadata.category, [1, 2, 1])
