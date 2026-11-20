# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_ds._core.visualizer.callbacks.config import update_appliance_visibility
from power_grid_model_ds._core.visualizer.callbacks.header import get_header_panel_styles
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML


def test_legend_is_visible_by_default():
    legend, search, config = get_header_panel_styles(None)

    assert legend["display"] == "flex"
    assert search["display"] == "none"
    assert config["display"] == "none"


def test_config_visibility_does_not_remove_other_panels():
    legend, search, config = get_header_panel_styles("btn-config")

    assert legend["display"] == "none"
    assert search["display"] == "none"
    assert config["display"] == "flex"


def test_search_visibility():
    legend, search, config = get_header_panel_styles("btn-search")

    assert legend["display"] == "none"
    assert search["display"] == "flex"
    assert config["display"] == "none"


def test_appliance_visibility_store():
    assert update_appliance_visibility(show_appliances=True) is True
    assert update_appliance_visibility(show_appliances=False) is False


def test_header_contains_all_persistent_panels():
    right_column = HEADER_HTML.children[1]
    panel_ids = {panel.id for panel in right_column.children}

    assert panel_ids == {
        "header-legend-panel",
        "header-search-panel",
        "header-config-panel",
    }
