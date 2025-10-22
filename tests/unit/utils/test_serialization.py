# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Comprehensive unit tests for Grid serialization with power-grid-model compatibility."""

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest
from numpy.typing import NDArray

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.utils.serialization import (
    _extract_extensions_data,
    _restore_extensions_data,
    load_grid_from_json,
    save_grid_to_json,
)
from power_grid_model_ds.arrays import LineArray
from power_grid_model_ds.arrays import NodeArray as BaseNodeArray


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


@pytest.fixture
def temp_dir():
    """Temporary directory fixture"""
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def basic_grid():
    """Basic grid fixture"""
    return Grid.from_txt("1 2", "2 3", "S10 1")


@pytest.fixture
def extended_grid():
    """Extended grid fixture with additional columns"""
    grid = ExtendedGrid.empty()
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


class TestSerializationFormats:
    """Test serialization across different formats and configurations"""

    @pytest.mark.parametrize("preserve_ext", [(True), (False)])
    def test_basic_serialization_roundtrip(self, basic_grid: Grid, temp_dir: Path, preserve_ext: bool):
        """Test basic serialization roundtrip for all formats"""
        path = temp_dir / "test.json"
        result_path = save_grid_to_json(basic_grid, path, preserve_extensions=preserve_ext)
        assert result_path.exists()

        # Load and verify
        loaded_grid = load_grid_from_json(path, target_grid_class=Grid)
        assert loaded_grid.node.size == basic_grid.node.size
        assert loaded_grid.line.size == basic_grid.line.size
        assert list(loaded_grid.node.id) == list(basic_grid.node.id)

    def test_extended_serialization_roundtrip(self, extended_grid: ExtendedGrid, temp_dir: Path):
        """Test extended serialization preserving custom data"""
        path = temp_dir / "extended.json"

        save_grid_to_json(extended_grid, path, preserve_extensions=True)
        loaded_grid = load_grid_from_json(path, target_grid_class=ExtendedGrid)

        # Verify core data
        assert loaded_grid.node.size == extended_grid.node.size
        assert loaded_grid.line.size == extended_grid.line.size

        # Verify extended data
        np.testing.assert_array_equal(loaded_grid.node.u, extended_grid.node.u)
        np.testing.assert_array_equal(loaded_grid.line.i_from, extended_grid.line.i_from)


class TestCrossTypeCompatibility:
    """Test cross-type loading and compatibility"""

    def test_basic_to_extended_loading(self, basic_grid: Grid, temp_dir: Path):
        """Test loading basic grid into extended type"""
        path = temp_dir / "basic.json"

        # Save basic grid
        save_grid_to_json(basic_grid, path)
        loaded_grid = load_grid_from_json(path, target_grid_class=ExtendedGrid)

        # Core data should transfer
        assert loaded_grid.node.size == basic_grid.node.size
        assert loaded_grid.line.size == basic_grid.line.size

    def test_extended_to_basic_loading(self, extended_grid: ExtendedGrid, temp_dir: Path):
        """Test loading extended grid into basic type"""
        path = temp_dir / "extended.json"

        # Save extended grid
        save_grid_to_json(extended_grid, path, preserve_extensions=True)
        loaded_grid = load_grid_from_json(path, target_grid_class=Grid)

        # Core data should transfer
        assert loaded_grid.node.size == extended_grid.node.size
        assert loaded_grid.line.size == extended_grid.line.size


class TestExtensionHandling:
    """Test extension data handling and edge cases"""

    def test_missing_extension_keys(self):
        """Test graceful handling of missing extension keys"""
        basic_grid = Grid.empty()

        # Test various malformed extension data
        test_cases = [
            {},  # Empty
            {"extended_columns": {}},  # Missing custom_arrays
            {"custom_arrays": {}},  # Missing extended_columns
            {"extended_columns": {"test": "value"}},  # Invalid structure
        ]

        for extensions in test_cases:
            # Should not raise
            _restore_extensions_data(basic_grid, extensions)

    def test_custom_array_serialization_roundtrip(self, temp_dir: Path):
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
        json_path = temp_dir / "custom_array.json"
        save_grid_to_json(grid, json_path, preserve_extensions=True)

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


class TestSpecialCases:
    """Test special cases and edge scenarios"""

    def test_empty_grid_handling(self, temp_dir: Path):
        """Test serialization of empty grids"""
        empty_grid = Grid.empty()

        json_path = temp_dir / "empty.json"

        # Should handle empty grids
        save_grid_to_json(empty_grid, json_path)

        # Should load back as empty
        loaded_json = load_grid_from_json(json_path, target_grid_class=Grid)
        assert loaded_json.node.size == 0

    def test_custom_array_extraction_edge_cases(self, temp_dir: Path):
        """Test edge cases in custom array extraction"""
        # Test with grid that has complex custom arrays that might cause extraction issues
        extended_grid = ExtendedGrid.empty()

        # Add data that might cause issues during extraction
        nodes = ExtendedNodeArray(
            id=[1, 2],
            u_rated=[10000, 10000],
            u=[float("nan"), float("inf")],  # Edge case values
        )
        extended_grid.append(nodes)

        # Should handle edge case values gracefully
        extensions = _extract_extensions_data(extended_grid)
        assert "extended_columns" in extensions
        assert "custom_arrays" in extensions

        # Test saving and loading with these edge cases
        json_path = temp_dir / "edge_cases.json"
        save_grid_to_json(extended_grid, json_path, preserve_extensions=True)

        # Should load without issues
        loaded_grid = load_grid_from_json(json_path, target_grid_class=Grid)
        assert loaded_grid.node.size == 2

    def test_invalid_extension_data_recovery(self, temp_dir: Path):
        """Test recovery from invalid extension data"""
        # Create valid extended grid
        extended_grid = ExtendedGrid.empty()
        nodes = ExtendedNodeArray(id=[1, 2], u_rated=[10000, 10000], u=[9950, 9900])
        extended_grid.append(nodes)

        json_path = temp_dir / "test_recovery.json"
        save_grid_to_json(extended_grid, json_path, preserve_extensions=True)

        # Corrupt extension data
        with open(json_path, "r") as f:
            data = json.load(f)

        # Add invalid extension data
        if "pgm_ds_extensions" in data:
            data["pgm_ds_extensions"]["extended_columns"]["node"]["u"] = [1, 2, 3, 4, 5]  # Wrong size
            data["pgm_ds_extensions"]["custom_arrays"]["fake"] = {"dtype": "invalid_dtype", "data": [[1, 2, 3]]}

        with open(json_path, "w") as f:
            json.dump(data, f)

        # Should load core data despite extension errors
        loaded_grid = load_grid_from_json(json_path, target_grid_class=Grid)
        assert loaded_grid.node.size == 2
