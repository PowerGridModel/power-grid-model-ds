# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Grid tests"""

import shutil
from pathlib import Path

import pytest

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.utils.pickle import save_to_pickle
from tests.fixtures.grid_classes import ExtendedGrid
from tests.fixtures.grids import build_basic_grid

# pylint: disable=missing-function-docstring


def test_cache_empty_grid(grid):
    """Test that empty grid can be cached"""
    cache_dir = Path("tmp")
    cache_name = "my_cache"
    cache_path = grid.cache(cache_dir=cache_dir, cache_name=cache_name, compress=False)

    assert cache_path.is_file()

    shutil.rmtree(cache_dir)


def test_cache_empty_grid_with_compression(grid):
    """Test that empty grid can be cached with compression"""
    cache_dir = Path("tmp")
    cache_name = "my_cache"
    cache_path = grid.cache(cache_dir=cache_dir, cache_name=cache_name, compress=True)

    assert cache_path.is_file()

    shutil.rmtree(cache_dir)


def test_cache_basic_grid(basic_grid):
    cache_dir = Path("tmp")
    cache_name = "my_cache"
    cache_path = basic_grid.cache(cache_dir=cache_dir, cache_name=cache_name, compress=False)

    assert cache_path.is_file()

    shutil.rmtree(cache_dir)


def test_cache_and_load_empty_grid(grid):
    """Test that empty grid can be loaded from cache"""
    cache_dir = Path("tmp")
    cache_name = "my_cache"
    cache_path = grid.cache(cache_dir=cache_dir, cache_name=cache_name, compress=False)

    new_grid = Grid.from_cache(cache_path)

    for old, new in zip(grid.all_arrays(), new_grid.all_arrays()):
        assert fp.array_equal(old, new)
    assert 0 == new_grid.graphs.active_graph.nr_nodes
    assert 0 == new_grid.graphs.complete_graph.nr_nodes
    shutil.rmtree(cache_dir)


def test_cache_and_load_basic_grid(basic_grid):
    cache_dir = Path("tmp")
    cache_path = basic_grid.cache(cache_dir=cache_dir, cache_name="my_cache", compress=False)

    new_grid = Grid.from_cache(cache_path)

    for old, new in zip(basic_grid.all_arrays(), new_grid.all_arrays()):
        assert fp.array_equal(old, new)
    assert basic_grid.graphs.active_graph.nr_nodes == new_grid.graphs.active_graph.nr_nodes
    assert basic_grid.graphs.complete_graph.nr_nodes == new_grid.graphs.complete_graph.nr_nodes
    shutil.rmtree(cache_dir)


def test_cache_and_load_basic_grid_with_compression(basic_grid):
    cache_dir = Path("tmp")
    cache_path = basic_grid.cache(cache_dir=cache_dir, cache_name="my_cache", compress=True)

    new_grid = Grid.from_cache(cache_path)
    assert isinstance(new_grid, Grid)

    for old, new in zip(basic_grid.all_arrays(), new_grid.all_arrays()):
        assert fp.array_equal(old, new)

    shutil.rmtree(cache_dir)


def test_cache_and_load_extended_grid():
    grid = ExtendedGrid.empty()
    grid = build_basic_grid(grid)

    cache_dir = Path("tmp")
    cache_name = "my_cache"
    cache_path = grid.cache(cache_dir=cache_dir, cache_name=cache_name, compress=False)

    new_grid = ExtendedGrid.from_cache(cache_path)

    for old, new in zip(grid.all_arrays(), new_grid.all_arrays()):
        assert fp.array_equal(old, new)
    assert grid.graphs.active_graph.nr_nodes == new_grid.graphs.active_graph.nr_nodes
    assert grid.graphs.complete_graph.nr_nodes == new_grid.graphs.complete_graph.nr_nodes
    assert hasattr(new_grid, "extra_value")
    shutil.rmtree(cache_dir)


def test_cache_and_load_after_node_deletion(basic_grid):
    node = basic_grid.node.get(id=106)
    basic_grid.delete_node(node)

    cache_dir = Path("tmp")
    cache_path = basic_grid.cache(cache_dir=cache_dir, cache_name="my_cache", compress=False)

    new_grid = Grid.from_cache(cache_path)

    for old, new in zip(basic_grid.all_arrays(), new_grid.all_arrays()):
        assert fp.array_equal(old, new)
    assert basic_grid.graphs.complete_graph.nr_nodes == new_grid.graphs.complete_graph.nr_nodes
    assert basic_grid.graphs.active_graph.nr_nodes == new_grid.graphs.active_graph.nr_nodes

    shutil.rmtree(cache_dir)


def test_load_invalid_grid():
    """Test that non-Grid objects cannot be loaded as grid."""
    cache_path = Path("tmp_dict.pickle")
    invalid_grid = {"name": "NOT A GRID"}
    save_to_pickle(path=cache_path, python_object=invalid_grid)
    with pytest.raises(TypeError):
        Grid.from_cache(cache_path)
    cache_path.unlink()
