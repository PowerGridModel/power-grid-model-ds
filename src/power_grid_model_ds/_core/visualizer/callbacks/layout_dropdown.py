from dash import Input, Output, callback


@callback(Output("cytoscape-graph", "layout"), Input("dropdown-update-layout", "value"), prevent_initial_call=True)
def update_layout(layout):
    """Callback to update the layout of the graph."""
    return {"name": layout, "animate": True}
