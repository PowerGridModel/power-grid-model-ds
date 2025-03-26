from dash import callback, Output, Input


@callback(Output('cytoscape-graph', 'layout'), Input('dropdown-update-layout', 'value'),
          prevent_initial_call=True)
def update_layout(layout):
    return {'name': layout, 'animate': True}