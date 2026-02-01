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
- Visualize attributes over a heatmap

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

This will start a local web server at <http://localhost:8050>

#### Examples

The visualizer has a minimal design at the moment.
Hence not all possibilities are directly mentioned in the UI. This section provides some handy tips to visualize common situations:

- All elements of a particular component type: Search -> Desired Component -> any attribute -> unassgined value (eg. Search -> `sym_power_sensor` -> `id` ->  `!=` ->  `-1`)
- All in-edges/out-edges for a particular node: Search -> `branches` -> `from_node` or `to_node` -> desired node.
- Voltage levels: Heatmap -> `node` -> `u_rated`
- Heatmap any result when an extended grid with result attribute is provided can be visualized.
  - Heatmap -> `node` -> `u_pu`
  - Heatmap -> `line` -> `loading`
  - Heatmap -> `node` -> `energized`

#### Disclaimer

Please note that the visualizer is still a work in progress and may not be fully functional or contain bugs.
We welcome any feedback or suggestions for improvement.
