# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Comprehensive unit tests for Grid serialization with power-grid-model compatibility."""

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np
import pytest
from numpy.typing import NDArray

from power_grid_model_ds import Grid
from power_grid_model_ds._core.load_flow import PowerGridModelInterface
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.utils.serialization import (
    _extract_extensions_data,
    _get_serialization_path,
    _restore_extensions_data,
    load_grid_from_json,
    load_grid_from_msgpack,
    save_grid_to_json,
    save_grid_to_msgpack,
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

    @pytest.mark.parametrize(
        "format_type,preserve_ext", [("json", True), ("json", False), ("msgpack", True), ("msgpack", False)]
    )
    def test_basic_serialization_roundtrip(
        self, basic_grid: Grid, temp_dir: Path, format_type: str, preserve_ext: bool
    ):
        """Test basic serialization roundtrip for all formats"""
        ext = "json" if format_type == "json" else "msgpack"
        path = temp_dir / f"test.{ext}"

        # Save
        if format_type == "json":
            result_path = save_grid_to_json(basic_grid, path, preserve_extensions=preserve_ext)
        else:
            result_path = save_grid_to_msgpack(basic_grid, path, preserve_extensions=preserve_ext)

        assert result_path.exists()

        # Load and verify
        if format_type == "json":
            loaded_grid = load_grid_from_json(path, target_grid_class=Grid)
        else:
            loaded_grid = load_grid_from_msgpack(path, target_grid_class=Grid)
        assert loaded_grid.node.size == basic_grid.node.size
        assert loaded_grid.line.size == basic_grid.line.size
        assert list(loaded_grid.node.id) == list(basic_grid.node.id)

    @pytest.mark.parametrize("format_type", ["json", "msgpack"])
    def test_extended_serialization_roundtrip(self, extended_grid: ExtendedGrid, temp_dir: Path, format_type: str):
        """Test extended serialization preserving custom data"""
        ext = "json" if format_type == "json" else "msgpack"
        path = temp_dir / f"extended.{ext}"

        # Save with extensions
        if format_type == "json":
            save_grid_to_json(extended_grid, path, preserve_extensions=True)
            loaded_grid = load_grid_from_json(path, target_grid_class=ExtendedGrid)
        else:
            save_grid_to_msgpack(extended_grid, path, preserve_extensions=True)
            loaded_grid = load_grid_from_msgpack(path, target_grid_class=ExtendedGrid)

        # Verify core data
        assert loaded_grid.node.size == extended_grid.node.size
        assert loaded_grid.line.size == extended_grid.line.size

        # Verify extended data
        np.testing.assert_array_equal(loaded_grid.node.u, extended_grid.node.u)
        np.testing.assert_array_equal(loaded_grid.line.i_from, extended_grid.line.i_from)

    def test_format_characteristics(self, basic_grid: Grid, temp_dir: Path):
        """Test format-specific characteristics"""
        json_path = temp_dir / "test.json"
        msgpack_path = temp_dir / "test.msgpack"

        save_grid_to_json(basic_grid, json_path)
        save_grid_to_msgpack(basic_grid, msgpack_path)

        # JSON should be human-readable
        with open(json_path) as f:
            json_data = json.load(f)
        assert "version" in json_data
        assert "data" in json_data

        # MessagePack should be more compact
        json_size = json_path.stat().st_size
        msgpack_size = msgpack_path.stat().st_size
        assert msgpack_size < json_size  # MessagePack is typically more compact


class TestCrossTypeCompatibility:
    """Test cross-type loading and compatibility"""

    @pytest.mark.parametrize("format_type", ["json", "msgpack"])
    def test_basic_to_extended_loading(self, basic_grid: Grid, temp_dir: Path, format_type: str):
        """Test loading basic grid into extended type"""
        ext = "json" if format_type == "json" else "msgpack"
        path = temp_dir / f"basic.{ext}"

        # Save basic grid
        if format_type == "json":
            save_grid_to_json(basic_grid, path)
            loaded_grid = load_grid_from_json(path, target_grid_class=ExtendedGrid)
        else:
            save_grid_to_msgpack(basic_grid, path)
            loaded_grid = load_grid_from_msgpack(path, target_grid_class=ExtendedGrid)

        # Core data should transfer
        assert loaded_grid.node.size == basic_grid.node.size
        assert loaded_grid.line.size == basic_grid.line.size

    @pytest.mark.parametrize("format_type", ["json", "msgpack"])
    def test_extended_to_basic_loading(self, extended_grid: ExtendedGrid, temp_dir: Path, format_type: str):
        """Test loading extended grid into basic type"""
        ext = "json" if format_type == "json" else "msgpack"
        path = temp_dir / f"extended.{ext}"

        # Save extended grid
        if format_type == "json":
            save_grid_to_json(extended_grid, path, preserve_extensions=True)
            loaded_grid = load_grid_from_json(path, target_grid_class=Grid)
        else:
            save_grid_to_msgpack(extended_grid, path, preserve_extensions=True)
            loaded_grid = load_grid_from_msgpack(path, target_grid_class=Grid)

        # Core data should transfer
        assert loaded_grid.node.size == extended_grid.node.size
        assert loaded_grid.line.size == extended_grid.line.size


class TestExtensionHandling:
    """Test extension data handling and edge cases"""

    def test_extension_extraction_and_restoration(self, extended_grid: ExtendedGrid):
        """Test extension data extraction and restoration"""
        # Extract extensions
        extensions = _extract_extensions_data(extended_grid)

        # Should have both types of extensions
        assert "extended_columns" in extensions
        assert "custom_arrays" in extensions

        # Should contain extended node data
        assert "node" in extensions["extended_columns"]
        assert "u" in extensions["extended_columns"]["node"]

        # Create new grid and restore
        new_grid = ExtendedGrid.empty()
        # Add basic structure first
        nodes = ExtendedNodeArray(id=[1, 2, 3], u_rated=[10500, 10500, 10500])
        new_grid.append(nodes)

        # Restore extensions
        _restore_extensions_data(new_grid, extensions)

        # Extended data should be restored
        np.testing.assert_array_equal(new_grid.node.u, extended_grid.node.u)

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

        # Test MessagePack serialization
        msgpack_path = temp_dir / "custom_array.msgpack"
        save_grid_to_msgpack(grid, msgpack_path, preserve_extensions=True)

        # Load back and verify
        loaded_grid_mp = load_grid_from_msgpack(msgpack_path, target_grid_class=GridWithCustomArray)

        # Verify core data
        assert loaded_grid_mp.node.size == 2
        np.testing.assert_array_equal(loaded_grid_mp.node.id, [1, 2])

        # Verify custom array was preserved
        assert hasattr(loaded_grid_mp, "custom_metadata")
        assert loaded_grid_mp.custom_metadata.size == 3
        np.testing.assert_array_equal(loaded_grid_mp.custom_metadata.id, [100, 200, 300])
        np.testing.assert_array_almost_equal(loaded_grid_mp.custom_metadata.metadata_value, [1.5, 2.5, 3.5])
        np.testing.assert_array_equal(loaded_grid_mp.custom_metadata.category, [1, 2, 1])


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.parametrize("format_type", ["json", "msgpack"])
    def test_file_not_found(self, format_type: str):
        """Test handling of missing files"""
        nonexistent_path = Path("nonexistent.") / format_type

        with pytest.raises(FileNotFoundError):
            if format_type == "json":
                load_grid_from_json(nonexistent_path)
            else:
                load_grid_from_msgpack(nonexistent_path)

    def test_corrupted_json_content(self, temp_dir: Path):
        """Test handling of corrupted JSON files"""
        json_path = temp_dir / "corrupted.json"

        with open(json_path, "w") as f:
            f.write("{ invalid json content")

        with pytest.raises(json.JSONDecodeError):
            load_grid_from_json(json_path)

    def test_corrupted_msgpack_data(self, temp_dir: Path):
        """Test handling of corrupted MessagePack files"""
        msgpack_path = temp_dir / "corrupted.msgpack"

        with open(msgpack_path, "wb") as f:
            f.write(b"invalid msgpack data")

        with pytest.raises(Exception):  # Could be various msgpack/power-grid-model exceptions
            load_grid_from_msgpack(msgpack_path)

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

    def test_io_permission_errors(self, temp_dir: Path):
        """Test I/O permission error handling"""
        basic_grid = Grid.empty()

        # Create read-only directory
        readonly_dir = temp_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        readonly_path = readonly_dir / "test.json"

        try:
            with pytest.raises((PermissionError, OSError)):
                save_grid_to_json(basic_grid, readonly_path)
        finally:
            readonly_dir.chmod(0o755)  # Cleanup


class TestUtilityFunctions:
    """Test utility functions and path handling"""

    @pytest.mark.parametrize(
        "input_path,format_type,expected",
        [
            ("test.json", "auto", "test.json"),
            ("test.msgpack", "auto", "test.msgpack"),
            ("test.mp", "auto", "test.mp"),
            ("test.xyz", "auto", "test.json"),  # Unknown defaults to JSON
            ("test.xyz", "json", "test.json"),
            ("test.xyz", "msgpack", "test.msgpack"),
        ],
    )
    def test_serialization_path_handling(self, input_path: str, format_type: str, expected: str):
        """Test path handling and format detection"""
        result = _get_serialization_path(Path(input_path), format_type)
        assert result == Path(expected)


class TestPowerGridModelIntegration:
    """Test integration with PowerGridModelInterface"""

    def test_interface_roundtrip(self, basic_grid: Grid, temp_dir: Path):
        """Test roundtrip through PowerGridModelInterface"""
        json_path = temp_dir / "interface_test.json"

        # Save and load through interface
        save_grid_to_json(basic_grid, json_path)

        # Should work with interface directly
        interface = PowerGridModelInterface(grid=basic_grid)
        input_data = interface.create_input_from_grid()

        # Create new grid from input data
        new_interface = PowerGridModelInterface(input_data=input_data)
        new_grid = new_interface.create_grid_from_input_data()

        assert new_grid.node.size == basic_grid.node.size

    def test_interface_error_propagation(self, temp_dir: Path):
        """Test error propagation from PowerGridModelInterface"""
        # This is harder to test directly, but we can verify errors are not swallowed
        basic_grid = Grid.empty()
        json_path = temp_dir / "error_test.json"

        # Create conditions that might cause interface errors
        with patch.object(PowerGridModelInterface, "create_input_from_grid", side_effect=Exception("PGM Error")):
            with pytest.raises(Exception, match="PGM Error"):
                save_grid_to_json(basic_grid, json_path)


class TestSpecialCases:
    """Test special cases and edge scenarios"""

    def test_empty_grid_handling(self, temp_dir: Path):
        """Test serialization of empty grids"""
        empty_grid = Grid.empty()

        json_path = temp_dir / "empty.json"
        msgpack_path = temp_dir / "empty.msgpack"

        # Should handle empty grids
        save_grid_to_json(empty_grid, json_path)
        save_grid_to_msgpack(empty_grid, msgpack_path)

        # Should load back as empty
        loaded_json = load_grid_from_json(json_path, target_grid_class=Grid)
        loaded_msgpack = load_grid_from_msgpack(msgpack_path, target_grid_class=Grid)

        assert loaded_json.node.size == 0
        assert loaded_msgpack.node.size == 0

    def test_extreme_values_handling(self, temp_dir: Path):
        """Test handling of extreme numeric values"""
        extended_grid = ExtendedGrid.empty()

        # Add nodes with extreme values
        nodes = ExtendedNodeArray(
            id=[1, 2],
            u_rated=[10000, 10000],
            u=[np.inf, -np.inf],  # Extreme values
        )
        extended_grid.append(nodes)

        json_path = temp_dir / "extreme.json"

        # Should handle extreme values (JSON supports inf)
        save_grid_to_json(extended_grid, json_path, preserve_extensions=True)
        loaded_grid = load_grid_from_json(json_path, target_grid_class=Grid)
        assert loaded_grid.node.size == 2

    def test_without_extensions_flag(self, extended_grid: ExtendedGrid, temp_dir: Path):
        """Test serialization without extensions flag"""
        json_path = temp_dir / "no_ext.json"
        msgpack_path = temp_dir / "no_ext.msgpack"

        # Save without extensions
        save_grid_to_json(extended_grid, json_path, preserve_extensions=False)
        save_grid_to_msgpack(extended_grid, msgpack_path, preserve_extensions=False)

        # Should load core data only
        loaded_json = load_grid_from_json(json_path, target_grid_class=Grid)
        loaded_msgpack = load_grid_from_msgpack(msgpack_path, target_grid_class=Grid)

        assert loaded_json.node.size == extended_grid.node.size
        assert loaded_msgpack.node.size == extended_grid.node.size

    def test_directory_creation_during_save(self, basic_grid: Grid, temp_dir: Path):
        """Test automatic directory creation during save operations"""
        # Test nested directory creation
        nested_json_path = temp_dir / "nested" / "deep" / "test.json"
        nested_msgpack_path = temp_dir / "nested" / "deep" / "test.msgpack"

        # Should create directories automatically
        save_grid_to_json(basic_grid, nested_json_path)
        save_grid_to_msgpack(basic_grid, nested_msgpack_path)

        assert nested_json_path.exists()
        assert nested_msgpack_path.exists()

        # Should be able to load back
        loaded_json = load_grid_from_json(nested_json_path, target_grid_class=Grid)
        loaded_msgpack = load_grid_from_msgpack(nested_msgpack_path, target_grid_class=Grid)

        assert loaded_json.node.size == basic_grid.node.size
        assert loaded_msgpack.node.size == basic_grid.node.size

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
