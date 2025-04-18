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

With Coordinates    | Hierarchical | Force-Directed
:------------------:|:------------:|:-------------:
<img width="250" alt="Coordinates" src="https://github.com/user-attachments/assets/6f991cb1-08b4-4c4b-8adc-eed36f58db40" /> | <img width="250" alt="Hierarchical" src="https://github.com/user-attachments/assets/0cf5684d-fb7c-4920-92b8-1e49bc827a92" />      |   <img width="250" alt="Force-Directed" src="https://github.com/user-attachments/assets/f0167ded-ceb4-4a31-a91e-e029dd6d7f13" />

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

#### Disclaimer
Please note that the visualizer is still a work in progress and may not be fully functional or contain bugs.
We welcome any feedback or suggestions for improvement.
