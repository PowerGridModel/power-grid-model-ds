# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from copy import copy
from pathlib import Path
from typing import TYPE_CHECKING

from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.utils.pickle import get_pickle_path, load_from_pickle, save_to_pickle
from power_grid_model_ds._core.utils.zip import file2gzip

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid


def load_grid_from_pickle(grid_class: type["Grid"], cache_path: Path, load_graphs: bool = True):
    """See Grid.from_cache()"""
    pickle_path = get_pickle_path(cache_path)
    grid = load_from_pickle(path=pickle_path)
    if not isinstance(grid, grid_class):
        raise TypeError(f"{pickle_path.name} is not a valid {grid_class.__name__} cache.")

    if load_graphs:
        grid.graphs = GraphContainer.from_arrays(grid)
    return grid


def save_grid_to_pickle(grid: "Grid", cache_dir: Path, cache_name: str, compress: bool = True):
    """See Grid.cache()"""
    tmp_graphs = copy(grid.graphs)
    grid.graphs = None  # noqa
    cache_dir.mkdir(parents=True, exist_ok=True)

    pickle_path = cache_dir / f"{cache_name}.pickle"
    save_to_pickle(path=pickle_path, python_object=grid)

    if compress:
        gzip_path = file2gzip(pickle_path)
        pickle_path.unlink()
        return gzip_path

    grid.graphs = tmp_graphs
    return pickle_path
