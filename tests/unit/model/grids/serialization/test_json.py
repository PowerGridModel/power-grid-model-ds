# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Comprehensive unit tests for Grid serialization with power-grid-model compatibility."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from power_grid_model.utils import json_serialize_to_file

from power_grid_model_ds import Grid, PowerGridModelInterface
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.containers.helpers import container_equal
from power_grid_model_ds._core.utils.misc import array_equal_with_nan
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

    @pytest.mark.parametrize("grid_fixture", ("basic_grid", "grid"))
    def test_serialization_roundtrip(self, request, grid_fixture: str, tmp_path: Path):
        """Test serialization roundtrip

        Scenarios:
        - Basic grid
        - Extended grid with extended arrays and additional non-array attributes
        - Empty grid
        """
        path = tmp_path / "grid.json"
        grid: Grid = request.getfixturevalue(grid_fixture)

        grid.serialize(path)
        loaded_grid = Grid.deserialize(path)
        assert loaded_grid == grid

    @pytest.mark.parametrize("grid_fixture", ("basic_grid", "grid"))
    def test_pgm_roundtrip(self, request, grid_fixture: str, tmp_path: Path):
        """Test roundtrip serialization for PGM-compatible grid"""
        # Grid
        grid: Grid = request.getfixturevalue(grid_fixture)

        # Replace nan values with dummy value. Otherwise PGM's json_serialize_to_file will remove these columns.
        grid.node.u_rated = 42

        grid.line.r1 = 42
        grid.line.x1 = 42
        grid.line.c1 = 42
        grid.line.tan1 = 42
        grid.line.i_n = 42

        input_data = PowerGridModelInterface(grid).create_input_from_grid()

        path = tmp_path / "input.json"
        json_serialize_to_file(path, input_data)

        loaded_grid = Grid.deserialize(path)

        loaded_input_data = PowerGridModelInterface(loaded_grid).create_input_from_grid()

        for array_name in input_data:
            original_array = input_data[array_name]
            loaded_array = loaded_input_data[array_name]

            assert array_equal_with_nan(original_array, loaded_array), f"Array '{array_name}' does not match"


class TestCrossTypeCompatibility:
    """Test cross-type loading and compatibility"""

    def test_basic_to_extended_loading(self, basic_grid: Grid, tmp_path: Path):
        """Test loading basic grid into extended type"""
        path = tmp_path / "basic.json"

        # Save basic grid
        basic_grid.serialize(path)
        loaded_grid = ExtendedGrid.deserialize(path)

        # Core data should transfer
        assert container_equal(basic_grid, loaded_grid, ignore_extras=True, fields_to_ignore=["graphs"])

    def test_extended_to_basic_loading(self, extended_grid: ExtendedGrid, tmp_path: Path, caplog):
        """Test loading extended grid into basic type"""
        path = tmp_path / "extended.json"

        # Save extended grid
        extended_grid.serialize(path)
        loaded_grid = Grid.deserialize(path)

        # Core data should transfer
        assert container_equal(loaded_grid, extended_grid, ignore_extras=True, fields_to_ignore=["graphs"])


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
        grid.serialize(json_path)

        # Load back and verify
        loaded_grid = GridWithCustomArray.deserialize(json_path)

        # Verify core data
        assert loaded_grid.node.size == 2
        np.testing.assert_array_equal(loaded_grid.node.id, [1, 2])

        # Verify custom array was preserved
        assert hasattr(loaded_grid, "custom_metadata")
        assert loaded_grid.custom_metadata.size == 3
        np.testing.assert_array_equal(loaded_grid.custom_metadata.id, [100, 200, 300])
        np.testing.assert_array_almost_equal(loaded_grid.custom_metadata.metadata_value, [1.5, 2.5, 3.5])
        np.testing.assert_array_equal(loaded_grid.custom_metadata.category, [1, 2, 1])


class TestDeserialize:
    def test_deserialize(self, tmp_path: Path):
        path = tmp_path / "json_data.json"

        data = {"node": [{"id": 1, "u_rated": 10000}, {"id": 2, "u_rated": 20000}]}

        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": data}, f)

        grid = Grid.deserialize(path)
        assert grid.node.size == 2

        assert grid.node.id.tolist() == [1, 2]
        assert grid.node.u_rated.tolist() == [10000, 20000]

    def test_extended_grid(self, tmp_path: Path, extended_grid: ExtendedGrid):
        extended_data = {
            "node": [{"id": 1, "u_rated": 10000, "analysis_flag": 42}, {"id": 2, "u_rated": 10000}],
            "value_extension": 4.2,
        }

        path = tmp_path / "json_data.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": extended_data}, f)

        grid = ExtendedGrid.deserialize(path)
        assert grid.value_extension == 4.2
        assert grid.node.analysis_flag.tolist() == [42, 0]

    def test_unexpected_field(self, tmp_path: Path):
        path = tmp_path / "incompatible.json"

        # Create incompatible JSON data
        incompatible_data = {
            "node": [{"id": 1, "u_rated": 10000}, {"id": 2, "u_rated": 10000}],
            "unexpected_field": "unexpected_value",
        }

        # Write incompatible data to file
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": incompatible_data}, f)

        grid = Grid.deserialize(path)
        assert not hasattr(grid, "unexpected_field")

    def test_missing_array_field(self, tmp_path: Path):
        path = tmp_path / "missing_array.json"

        # Node data does not contain 'id' field
        missing_array_data = {
            "node": [{"u_rated": 10000}, {"u_rated": 10000}],
        }

        # Write data to file
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": missing_array_data}, f)

        grid = Grid.deserialize(path)
        assert grid.line.size == 0  # line array should be empty

    def test_some_records_miss_data(self, tmp_path):
        path = tmp_path / "incomplete_array.json"
        incomplete_data = {
            "node": [{"id": 1, "u_rated": 10000}, {"u_rated": 10000}, {"id": 3}],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump({"data": incomplete_data}, f)

        with pytest.raises(KeyError):
            Grid.deserialize(path)

