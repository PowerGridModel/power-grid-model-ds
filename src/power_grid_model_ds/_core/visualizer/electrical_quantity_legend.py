# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Build the electrical quantity legend displayed above the graph."""

from dash import html

from power_grid_model_ds._core.visualizer.electrical_quantity_styling import (
    MISSING_COLOR,
    RAINBOW_STOPS,
)

QUANTITY_LABELS = {
    "u_pu": ("Voltage magnitude", "p.u."),
    "u_angle": ("Voltage angle", "rad"),
}


def _rgb_to_hex(color: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a CSS hexadecimal colour."""
    return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def build_electrical_legend(  # noqa: PLR0913 - supports legacy fields and summary callers
    scenario_index: int,
    minimum: float | None = None,
    maximum: float | None = None,
    missing_count: int = 0,
    *,
    summary: dict[str, float | int | None] | None = None,
    quantity: str = "u_pu",
    component_group: str = "node",
) -> html.Div:
    """Create a labelled legend for the selected node quantity."""
    if summary is not None:
        minimum = summary.get("minimum")
        maximum = summary.get("maximum")
        missing_count = int(summary.get("missing_count") or 0)
    quantity_label, unit = QUANTITY_LABELS.get(quantity, (quantity, ""))
    unit_suffix = f" ({unit})" if unit else ""
    component_label = "nodes" if component_group == "node" else f"{component_group.replace('_', ' ')} elements"

    has_values = minimum is not None and maximum is not None
    has_range = has_values and minimum != maximum

    statistics = html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "Minimum",
                        className="electrical-stat-label",
                    ),
                    html.Strong(
                        f"{minimum:.4f}" if minimum is not None else "N/A",
                        className="electrical-stat-value",
                    ),
                ],
                className="electrical-stat",
            ),
            html.Div(
                [
                    html.Span(
                        "Maximum",
                        className="electrical-stat-label",
                    ),
                    html.Strong(
                        f"{maximum:.4f}" if maximum is not None else "N/A",
                        className="electrical-stat-value",
                    ),
                ],
                className="electrical-stat",
            ),
            html.Div(
                [
                    html.Span(
                        f"Missing {component_label}",
                        className="electrical-stat-label",
                    ),
                    html.Strong(
                        str(missing_count),
                        className="electrical-stat-value",
                    ),
                ],
                className="electrical-stat",
            ),
        ],
        className="electrical-legend-statistics",
    )

    content = [
        html.H3(
            f"{quantity_label}{unit_suffix} - Scenario {scenario_index + 1}",
            className="electrical-legend-title",
        ),
        statistics,
    ]

    if has_range:
        content.extend(
            [
                html.Div(
                    "Relative value colour scale",
                    className="electrical-scale-title",
                ),
                html.Div(
                    className="electrical-scale-bar",
                    style={
                        "background": (
                            "linear-gradient(to right, "
                            + ", ".join(
                                f"{_rgb_to_hex(color)} {index * 100 / (len(RAINBOW_STOPS) - 1):.3f}%"
                                for index, color in enumerate(RAINBOW_STOPS)
                            )
                            + ")"
                        ),
                    },
                    role="img",
                    **{
                        "aria-label": (
                            f"Colour scale from {minimum:.4f} {unit} in purple to {maximum:.4f} {unit} in red."
                        ),
                    },
                ),
                html.Div(
                    [
                        html.Span(f"Low: {minimum:.4f} {unit}"),
                        html.Span(f"High: {maximum:.4f} {unit}"),
                    ],
                    className="electrical-scale-endpoints",
                ),
            ]
        )

    elif has_values:
        content.append(
            html.P(
                "All displayed values are equal. A single midpoint colour is used.",
                className="electrical-legend-note",
            )
        )

    else:
        content.append(
            html.P(
                f"No {quantity_label.lower()} values are available for the displayed {component_label}.",
                className="electrical-legend-note",
            )
        )

    if missing_count:
        content.append(
            html.Div(
                [
                    html.Span(
                        className="electrical-missing-swatch",
                        style={
                            "backgroundColor": MISSING_COLOR,
                        },
                        **{
                            "aria-hidden": "true",
                        },
                    ),
                    html.Span(f"Grey indicates missing values ({missing_count} {component_label})."),
                ],
                className="electrical-missing-description",
            )
        )

    content.append(
        html.P(
            "Colours show relative values only; they do not establish whether an electrical value is acceptable.",
            className="electrical-legend-note",
        )
    )

    return html.Div(
        content,
        className="electrical-legend-content",
    )
