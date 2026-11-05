"""Manual demonstration of F05 timestamp-based network-state inspection.

Run from the repository root:

    python examples/visualizer/f05_timestamp_selection_demo.py

Open http://127.0.0.1:8050 and select Node 1.
The displayed values are synthetic demonstration data, not results
calculated by a state estimator.
"""

from power_grid_model import (
    AttributeType,
    ComponentType,
    DatasetType,
    initialize_array,
)

from power_grid_model_ds.visualizer import visualize
from tests.integration.visualizer_tests import get_coordinated_three_phase_grid

TIMESTAMPS = (
    "2026-11-05T09:00:00+01:00",
    "2026-11-05T09:15:00+01:00",
    "2026-11-05T09:30:00+01:00",
    "2026-11-05T09:45:00+01:00",
)


def main() -> None:
    """Launch the visualiser with four known scenarios."""
    grid = get_coordinated_three_phase_grid()

    updates = initialize_array(
        DatasetType.update,
        ComponentType.line,
        (4, 2),
    )
    updates[AttributeType.id] = grid.line.id[:2]
    updates[AttributeType.from_status][:] = 1
    updates[AttributeType.from_status][1, 0] = 0

    output = initialize_array(
        DatasetType.asym_output,
        ComponentType.node,
        (4, 3),
    )
    output[AttributeType.id] = grid.node.id[:3]

    output[AttributeType.u] = [
        [
            [401.0, 402.0, 403.0],
            [404.0, 405.0, 406.0],
            [407.0, 408.0, 409.0],
        ],
        [
            [410.0, 411.0, 412.0],
            [413.0, 414.0, 415.0],
            [416.0, 417.0, 418.0],
        ],
        [
            [419.0, 420.0, 421.0],
            [422.0, 423.0, 424.0],
            [425.0, 426.0, 427.0],
        ],
        [
            [428.0, 429.0, 430.0],
            [431.0, 432.0, 433.0],
            [434.0, 435.0, 436.0],
        ],
    ]

    output[AttributeType.energized][:] = 1

    print("F05 manual demonstration")
    print("URL: http://127.0.0.1:8050")
    print("Available timestamps:")
    for timestamp in TIMESTAMPS:
        print(f"  {timestamp}")

    print("Select Node 1 in the network topology.")
    print("Expected phase values at 09:00: 401.0, 402.0, 403.0")
    print("Expected phase values at 09:45: 428.0, 429.0, 430.0")

    visualize(
        grid=grid,
        update_data={ComponentType.line: updates},
        output_data={ComponentType.node: output},
        timestamps=TIMESTAMPS,
        debug=False,
        port=8050,
    )


if __name__ == "__main__":
    main()
