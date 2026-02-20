# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import numpy as np

YELLOW = "#facc37"
CYTO_COLORS = {
    "line": YELLOW,
    "link": "#008000",
    "transformer": "#4290f5",
    "node": YELLOW,
    "generic_branch": "#dddddd",
    "asym_line": "#2de2ca",
    "selected": "#e28743",
    "selected_transformer": "#0349a3",
    "selected_link": "#004000",
    "selected_generic_branch": "#9e9e9e",
    "selected_asym_line": "#1D9181",
    "substation_node": "purple",
    "open_branch": "#c9c9c9",
    "highlighted": "#a10000",
    "heatmap_min": "#4A90E2",  # viridis low - blue
    "heatmap_max": "#F5D76E",  # viridis high - yellow
    "heatmap_mid": "#E8644E",  # viridis mid - orange
}
BACKGROUND_COLOR = "#555555"


def _map_colors_to_array(values: np.ndarray) -> list[str]:
    """Map numerical values to heatmap colors using predefined color palette.

    Uses colors defined in CYTO_COLORS:
    - Low values: heatmap_min
    - Mid values: heatmap_mid
    - High values: heatmap_max

    Args:
        values: Array of numerical values to map to colors.

    Returns:
        List of hex color strings corresponding to each value.
    """
    if len(values) == 0:
        return []

    # Convert hex colors to RGB arrays
    def _hex_to_rgb(hex_color: str) -> np.ndarray:
        hex_color = hex_color.lstrip("#")
        return np.array([int(hex_color[i : i + 2], 16) for i in (0, 2, 4)])

    rgb_min = _hex_to_rgb(CYTO_COLORS["heatmap_min"])
    rgb_mid = _hex_to_rgb(CYTO_COLORS["heatmap_mid"])
    rgb_max = _hex_to_rgb(CYTO_COLORS["heatmap_max"])

    # Handle case where all values are the same
    min_val = values.min()
    max_val = values.max()

    if min_val == max_val:
        return [CYTO_COLORS["heatmap_mid"]] * len(values)

    # Normalize values to [0, 1]
    normalized = (values - min_val) / (max_val - min_val)

    # Vectorized three-way interpolation
    # For values <= 0.5: interpolate between min and mid
    # For values > 0.5: interpolate between mid and max
    mask_low = normalized <= 0.5

    # Compute interpolation factors (t) for both ranges
    t = np.where(mask_low, normalized * 2, (normalized - 0.5) * 2)

    # Select start and end colors based on the range
    color1 = np.where(mask_low[:, None], rgb_min, rgb_mid)
    color2 = np.where(mask_low[:, None], rgb_mid, rgb_max)

    # Vectorized linear interpolation: color1 + t * (color2 - color1)
    rgb_values = (color1 + t[:, None] * (color2 - color1)).astype(int)

    # Convert RGB arrays to hex strings
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in rgb_values]
