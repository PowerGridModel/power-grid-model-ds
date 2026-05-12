<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Visualizer

## Features

- Based on [dash-cytoscape](https://github.com/plotly/dash-cytoscape).
- Visualize small and large (10000+ nodes) networks 
- Explore attributes of nodes and branches
- Highlight specific nodes and branches
- Visualize various layouts, including hierarchical, force-directed and coordinate-based layouts
- Export as a standalone HTML file for sharing or offline viewing

With Coordinates    | Hierarchical | Force-Directed
:------------------:|:------------:|:-------------:
<img width="250" alt="Coordinates" src="_static/grid-with-coordinates.png" /> | <img width="250" alt="Hierarchical" src="_static/grid-hierarchical.png" />      |   <img width="250" alt="Force-Directed" src="_static/grid-force-directed.png" />

----- 
## Quickstart
#### Installation
```bash
pip install 'power-grid-model-ds[visualizer]'  # quotes added for zsh compatibility
```

#### Usage
```python
from power_grid_model_ds import Grid
from power_grid_model_ds.visualizer import visualize
from power_grid_model_ds.generators import RadialGridGenerator

grid = RadialGridGenerator(Grid).run()
visualize(grid)
```
This will start a local web server at http://localhost:8050

#### Saving to HTML

To save a visualization as a standalone HTML file that can be shared or opened later without a running Python server, this does not contain advanced interaction but the graph only:

```python
from power_grid_model_ds import Grid
from power_grid_model_ds.visualizer import save_html
from power_grid_model_ds.generators import RadialGridGenerator

grid = RadialGridGenerator(Grid).run()
save_html(grid, "my_grid.html")

# With options:
save_html(grid, "my_grid.html", layout="cose", include_appliances=True)
```

The generated file embeds the graph data and [Cytoscape.js](https://js.cytoscape.org/) and supports pan, zoom, and click interactions in any browser.

#### Disclaimer
Please note that the visualizer is still a work in progress and may not be fully functional or contain bugs.
We welcome any feedback or suggestions for improvement.
