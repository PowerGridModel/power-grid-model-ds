# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from pathlib import Path

try:
    import dash_bootstrap_components as dbc
    from dash import Dash
    from dash_bootstrap_components.icons import FONT_AWESOME

    from power_grid_model_ds import Grid
    from power_grid_model_ds._core.visualizer import server_state
    from power_grid_model_ds._core.visualizer.app import GOOGLE_FONTS, MDBOOTSTRAP, get_app_layout
    from power_grid_model_ds._core.visualizer.html_export import generate_standalone_html
    from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
    from power_grid_model_ds._core.visualizer.layout.header_config import LayoutOptions
    from power_grid_model_ds._core.visualizer.layout.layout_config import get_default_graph_layout, layout_with_config
    from power_grid_model_ds._core.visualizer.parsers import parse_element_data
    from power_grid_model_ds._core.visualizer.parsing_utils import filter_out_appliances
except ImportError as error:
    raise ImportError(
        "Missing dependencies for visualizer: install with 'pip install power-grid-model-ds[visualizer]'"
    ) from error


def save_html(
    grid: Grid,
    path: str | Path,
    *,
    layout: str = "",
    include_appliances: bool = False,
    title: str = "Power Grid Model Visualization",
) -> None:
    """Save the Grid visualization as a standalone HTML file.

    The file can be opened in any browser without a running Python server
    and supports pan, zoom, and click interactions via Cytoscape.js.

    grid: Grid
        The grid to visualize.
    path: str | Path
        Output path for the HTML file.
    layout: str
        Layout algorithm to use. If not provided, uses preset (when x/y coords are present)
        or breadthfirst. Other options: "random", "circle", "concentric", "grid", "cose".
    include_appliances: bool
        Whether to include appliance nodes (loads, generators, sources). Default: False.
    title: str
        Title shown in the browser tab. Default: "Power Grid Model Visualization".
    """
    viz_elements_dict = parse_element_data(grid)
    all_elements = viz_elements_dict.values()
    elements = list(all_elements if include_appliances else filter_out_appliances(all_elements))
    for element in elements:
        element["data"].pop("associated_ids", None)

    layout_option = LayoutOptions(layout) if layout else get_default_graph_layout(grid.node)
    layout_config = layout_with_config(layout_option, source_available=grid.source.size != 0)

    html_content = generate_standalone_html(elements, DEFAULT_STYLESHEET, layout_config, title=title)
    Path(path).write_text(html_content, encoding="utf-8")


def visualize(grid: Grid, debug: bool = False, port: int = 8050) -> None:
    """Visualize the Grid.

    grid: Grid
        The grid to visualize.

    layout: str
        The layout to use.

        If 'layout' is not provided (""):
            And grid.node contains "x" and "y" columns:
                The layout will be set to "preset" which uses the x and y coordinates to place the nodes.
            Otherwise:
                The layout will be set to "breadthfirst", which is a hierarchical breadth-first-search (BFS) layout.
        Other options:
            - "random": A layout that places the nodes randomly.
            - "circle": A layout that places the nodes in a circle.
            - "concentric": A layout that places the nodes in concentric circles.
            - "grid": A layout that places the nodes in a grid matrix.
            - "cose": A layout that uses the CompoundSpring Embedder algorithm (force-directed layout)
    """
    # Store Grid object on server side (thread-safe)
    server_state.set_grid(grid)

    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, MDBOOTSTRAP, FONT_AWESOME, GOOGLE_FONTS]
    )
    app.layout = get_app_layout(grid)
    app.run(debug=debug, port=port, threaded=False)
