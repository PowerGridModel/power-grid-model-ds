# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Build the electrical quantity legend displayed above the graph."""

from dash import html

from power_grid_model_ds._core.visualizer.electrical_quantity_styling import (
    HIGH_COLOR,
    LOW_COLOR,
    MISSING_COLOR,
)

QUANTITY_LABELS = {
    "u_pu": ("Voltage magnitude", "p.u."),
    "u_angle": ("Voltage angle", "rad"),
}


def _rgb_to_hex(color: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a CSS hexadecimal colour."""
    return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def build_electrical_legend(
    scenario_index: int,
    minimum: float | None,
    maximum: float | None,
    missing_count: int,
    quantity: str = "u_pu",
) -> html.Div:
    """Create a labelled legend for the selected node quantity."""
    if quantity not in QUANTITY_LABELS:
        raise ValueError(f"Unsupported electrical quantity: {quantity}")

    quantity_label, unit = QUANTITY_LABELS[quantity]

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
                        "Missing nodes",
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
            f"{quantity_label} ({unit}) - Scenario {scenario_index + 1}",
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
                            f"linear-gradient(to right, {_rgb_to_hex(LOW_COLOR)}, {_rgb_to_hex(HIGH_COLOR)})"
                        ),
                    },
                    role="img",
                    **{
                        "aria-label": (
                            f"Colour scale from {minimum:.4f} {unit} in blue to {maximum:.4f} {unit} in red."
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
                f"No {quantity_label.lower()} values are available for the displayed nodes.",
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
                    html.Span(f"Grey indicates missing values ({missing_count} nodes)."),
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
