# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from power_grid_model_ds.visualizer import save_html
from tests.fixtures.grids import build_basic_grid


@pytest.fixture
def basic_grid(grid):
    return build_basic_grid(grid)


def test_save_html_defaults(tmp_path, basic_grid):
    path = tmp_path / "grid.html"
    save_html(basic_grid, path)
    content = path.read_text()

    assert path.exists()
    assert "breadthfirst" in content


def test_save_html_options(tmp_path, basic_grid):
    path = tmp_path / "grid.html"
    save_html(basic_grid, path, layout="cose", include_appliances=True)
    content = path.read_text()

    assert "cose" in content

    path_no_appliances = tmp_path / "no_appliances.html"
    save_html(basic_grid, path_no_appliances, include_appliances=False)
    assert path.stat().st_size > path_no_appliances.stat().st_size
