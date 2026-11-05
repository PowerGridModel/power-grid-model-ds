"""F05 selected-timestamp network-state inspection."""

import math
from typing import Any

from dash import Input, Output, callback, html
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.server_state import (
    get_output_data,
    get_timestamps,
    get_update_data,
)
from power_grid_model_ds._core.visualizer.timestamp_selection import get_component_state


def _selected_components(
    node_data: list[dict[str, Any]] | None,
    edge_data: list[dict[str, Any]] | None,
) -> list[tuple[ComponentType, int]]:
    """Resolve Cytoscape selections to unique PGM component identifiers."""
    selected: list[tuple[ComponentType, int]] = []
    seen: set[tuple[ComponentType, int]] = set()

    for element in (node_data or []) + (edge_data or []):
        for group, ids in element.get("associated_ids", {}).items():
            try:
                component_type = ComponentType(group)
            except ValueError:
                continue

            for component_id in ids:
                key = (component_type, int(component_id))
                if key not in seen:
                    seen.add(key)
                    selected.append(key)

    return selected


PHASE_LABELS = ("A", "B", "C")


def _format_value(value: object) -> str:
    """Format values and distinguish three-phase quantities."""
    if isinstance(value, list):
        if len(value) == len(PHASE_LABELS) and all(not isinstance(item, list) for item in value):
            return ", ".join(f"{phase}: {_format_value(item)}" for phase, item in zip(PHASE_LABELS, value, strict=True))
        return ", ".join(_format_value(item) for item in value)

    if isinstance(value, float) and not math.isfinite(value):
        return "Unavailable (non-finite value)"

    return str(value)


def _is_unavailable(value: object) -> bool:
    """Check whether a scalar or all elements of a quantity are unavailable."""
    if isinstance(value, list):
        return bool(value) and all(_is_unavailable(item) for item in value)
    return isinstance(value, float) and not math.isfinite(value)


def _quantity_card(attribute: str, value: list[Any]) -> html.Div:
    """Display three-phase values without a wide attribute table."""
    phases = [
        html.Div(
            [
                html.Span(
                    f"Phase {phase}",
                    className="d-block text-muted small mb-1",
                ),
                html.Strong(
                    _format_value(phase_value),
                    className="d-block",
                    style={"overflowWrap": "anywhere"},
                ),
            ],
            className="col-4",
        )
        for phase, phase_value in zip(PHASE_LABELS, value, strict=True)
    ]

    return html.Div(
        [
            html.Div(
                attribute,
                className="fw-semibold mb-3",
            ),
            html.Div(phases, className="row g-2"),
        ],
        className="rounded-3 border p-3 mb-3 bg-light",
        **{"data-attribute": attribute},
    )


def _scalar_row(attribute: str, value: object) -> html.Div:
    """Render an available scalar or non-phase quantity."""
    return html.Div(
        [
            html.Span(attribute, className="text-muted"),
            html.Strong(
                _format_value(value),
                style={"overflowWrap": "anywhere", "textAlign": "right"},
            ),
        ],
        className="d-flex justify-content-between gap-3 py-2 border-bottom",
        **{"data-attribute": attribute},
    )


def _state_card(
    label: str,
    dataset: Any,
    component_type: ComponentType,
    component_id: int,
    scenario_index: int,
) -> html.Div:
    """Render available component values and summarise unavailable attributes."""
    heading = html.H6(label, className="fw-semibold mb-3")

    if dataset is None or component_type not in dataset:
        return html.Div(
            [
                heading,
                html.Div(
                    "No data available for this component.",
                    className="text-muted small rounded-3 bg-light p-3",
                ),
            ],
            className="mb-4",
        )

    state = get_component_state(
        dataset,
        component_type,
        component_id,
        scenario_index,
    )

    if state is None:
        return html.Div(
            [
                heading,
                html.Div(
                    "Component result unavailable at this timestamp.",
                    className="text-muted small rounded-3 bg-light p-3",
                ),
            ],
            className="mb-4",
        )

    available = []
    unavailable = []

    for attribute, value in state.items():
        if _is_unavailable(value):
            unavailable.append(attribute)
        elif (
            isinstance(value, list)
            and len(value) == len(PHASE_LABELS)
            and all(not isinstance(item, list) for item in value)
        ):
            available.append(_quantity_card(attribute, value))
        else:
            available.append(_scalar_row(attribute, value))

    if not available:
        available.append(html.P("No available values.", className="text-muted small"))

    if unavailable:
        available.append(
            html.Details(
                [
                    html.Summary(
                        f"Unavailable attributes ({len(unavailable)})",
                        className="small fw-semibold",
                        style={"cursor": "pointer"},
                    ),
                    html.P(
                        ", ".join(unavailable),
                        className="text-muted small mt-2 mb-0",
                    ),
                ],
                className="rounded-3 border p-3 mt-3",
            )
        )

    return html.Div(
        [heading, *available],
        className="mb-4",
    )


def build_timestamp_state(
    scenario_index: int | None,
    node_data: list[dict[str, Any]] | None,
    edge_data: list[dict[str, Any]] | None,
) -> html.Div | str:
    """Render selected component values at the selected scenario."""
    timestamps = get_timestamps()

    if timestamps is None:
        return "Timestamp metadata is unavailable."

    if (
        not isinstance(scenario_index, int)
        or isinstance(scenario_index, bool)
        or not 0 <= scenario_index < len(timestamps)
    ):
        return "Select an available timestamp."

    components = _selected_components(node_data, edge_data)

    if not components:
        return html.Div(
            [
                html.I(className="fas fa-mouse-pointer me-2"),
                html.Span("No component selected"),
            ],
            className="text-muted small py-2",
        )

    output_data = get_output_data()
    update_data = get_update_data()

    sections = []

    for component_type, component_id in components:
        sections.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.H5(
                                f"{component_type.value.capitalize()} - ID {component_id}",
                                className="fw-semibold mb-0",
                            ),
                            html.Span(
                                component_type.value.capitalize(),
                                className="badge rounded-pill bg-light text-dark border",
                            ),
                        ],
                        className="d-flex justify-content-between align-items-center gap-2 mb-4",
                    ),
                    _state_card(
                        "Output data",
                        output_data,
                        component_type,
                        component_id,
                        scenario_index,
                    ),
                    _state_card(
                        "Update data",
                        update_data,
                        component_type,
                        component_id,
                        scenario_index,
                    ),
                ],
                className="border rounded-3 p-3 p-md-4 mb-3",
            )
        )

    return html.Div(sections)


@callback(
    Output("timestamp-state-output", "children"),
    Input("timestamp-selector", "value"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def update_timestamp_state(
    scenario_index: int | None,
    node_data: list[dict[str, Any]] | None,
    edge_data: list[dict[str, Any]] | None,
) -> html.Div | str:
    """Refresh the selected component state when time or selection changes."""
    return build_timestamp_state(scenario_index, node_data, edge_data)


@callback(
    Output("timestamp-time", "options"),
    Output("timestamp-time", "value"),
    Input("timestamp-date", "date"),
)
def update_available_times(
    selected_date: str | None,
) -> tuple[list[dict[str, str | int]], int | None]:
    """Show only times belonging to the selected calendar date."""
    timestamps = get_timestamps()

    if timestamps is None or selected_date is None:
        return [], None

    options = [
        {
            "label": timestamp[11:],
            "value": index,
        }
        for index, timestamp in enumerate(timestamps)
        if timestamp[:10] == selected_date
    ]

    if not options:
        return [], None

    return options, int(options[0]["value"])


@callback(
    Output("timestamp-selector", "value"),
    Input("timestamp-time", "value"),
)
def update_selected_scenario(
    scenario_index: int | None,
) -> int | None:
    """Preserve the original timestamp-to-scenario mapping."""
    timestamps = get_timestamps()

    if timestamps is None:
        return None

    if (
        not isinstance(scenario_index, int)
        or isinstance(scenario_index, bool)
        or not 0 <= scenario_index < len(timestamps)
    ):
        return None

    return scenario_index
