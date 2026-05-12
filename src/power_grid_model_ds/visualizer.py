# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

try:
    import dash_bootstrap_components as dbc
    from dash import Dash
    from dash_bootstrap_components.icons import FONT_AWESOME

    from power_grid_model_ds import Grid
    from power_grid_model_ds._core.visualizer import server_state
    from power_grid_model_ds._core.visualizer.app import GOOGLE_FONTS, MDBOOTSTRAP, get_app_layout
    from power_grid_model_ds._core.visualizer.grid_utils import dynamic_grid_obj_from_grid, extend_grid_dynamically
except ImportError as error:
    raise ImportError(
        "Missing dependencies for visualizer: install with 'pip install power-grid-model-ds[visualizer]'"
    ) from error


def visualize(grid: Grid, update_data=None, output_data=None, debug: bool = False, port: int = 8050) -> None:
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
    if update_data is not None and output_data is not None:
        dynamic_class_update = extend_grid_dynamically(type(grid), extra_dataset=update_data)
        dynamic_class_update_output = extend_grid_dynamically(dynamic_class_update, extra_dataset=output_data)
        grid_obj = dynamic_grid_obj_from_grid(dynamic_class_update_output, grid)
    elif update_data is None and output_data is not None:
        grid_obj = dynamic_grid_obj_from_grid(extend_grid_dynamically(type(grid), extra_dataset=output_data), grid)
    elif output_data is None and update_data is not None:
        grid_obj = dynamic_grid_obj_from_grid(extend_grid_dynamically(type(grid), extra_dataset=update_data), grid)
    else:
        grid_obj = grid

    server_state.set_app_state(grid_obj, update_data, output_data)

    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, MDBOOTSTRAP, FONT_AWESOME, GOOGLE_FONTS]
    )
    app.layout = get_app_layout(grid)
    app.run(debug=debug, port=port, threaded=False)
