# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import json
from typing import Any

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/cytoscape@3/dist/cytoscape.min.js"></script>
  <style>
    body {{ margin: 0; background: {background_color}; }}
    #cy {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="cy"></div>
  <script>
    cytoscape({{
      container: document.getElementById('cy'),
      elements: {elements_json},
      style: {stylesheet_json},
      layout: {layout_json}
    }});
  </script>
</body>
</html>
"""


def generate_standalone_html(
    elements: list[dict[str, Any]],
    stylesheet: list[dict[str, Any]],
    layout: dict[str, Any],
) -> str:
    """Generate a standalone HTML string with an interactive Cytoscape.js graph."""
    return _HTML_TEMPLATE.format(
        background_color=BACKGROUND_COLOR,
        elements_json=json.dumps(elements),
        stylesheet_json=json.dumps(stylesheet),
        layout_json=json.dumps(layout),
    )
