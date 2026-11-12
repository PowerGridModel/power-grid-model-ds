# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Manual verification of F05 scenario-based network-state inspection.

Run from the repository root:

    python -m examples.visualizer.f05_manual_test --timestamps
    python -m examples.visualizer.f05_manual_test --no-timestamps

The demonstration uses synthetic data and does not run state estimation.
"""

import argparse

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


def build_demo_data():
    """Build a four-scenario dataset with known inputs and outputs."""
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
    output[AttributeType.energized][1, 2] = 0

    return grid, updates, output


def print_test_plan(with_timestamps: bool, grid) -> None:
    """Print the expected results for manual browser verification."""
    first_node = int(grid.node.id[0])
    first_line = int(grid.line.id[0])
    third_node = int(grid.node.id[2])

    print("\nF05 MANUAL VERIFICATION")
    print("=" * 60)
    print("URL: http://127.0.0.1:8050")
    print("Timestamps:", "enabled" if with_timestamps else "disabled")
    print("Synthetic data only; no state estimation is executed.")

    print("\n1. SCENARIO SELECTION")
    print("   Initial scenario index: empty")
    print("   Enter 1 and press Enter: scenario 1 remains selected")
    print("   Enter -1: validation error")
    print("   Enter 4: validation error")
    print("   Clear the index: normal component inspection returns")

    print("\n2. NODE OUTPUTS")
    print(f"   Select node ID {first_node}")
    for index, voltages in enumerate(
        (
            (401.0, 402.0, 403.0),
            (410.0, 411.0, 412.0),
            (419.0, 420.0, 421.0),
            (428.0, 429.0, 430.0),
        )
    ):
        print(f"   Scenario {index}: output u = {voltages}")

    print("\n3. LINE INPUT UPDATES")
    print(f"   Select line ID {first_line}")
    print("   Scenario 0: from_status = 1")
    print("   Scenario 1: from_status = 0")
    print("   Scenario 2: from_status = 1")
    print("   Scenario 3: from_status = 1")

    print("\n4. VALID ZERO OUTPUT")
    print(f"   Select node ID {third_node}")
    print("   Scenario 1: output energized = 0")

    if with_timestamps:
        print("\n5. TIMESTAMP NAVIGATION")
        for index, timestamp in enumerate(TIMESTAMPS):
            print(f"   Scenario {index}: {timestamp}")
        print("   Selecting a timestamp updates the scenario index")
        print("   Entering a scenario index updates date and time")
        print("   Clearing the scenario index resets timestamp selection")
    else:
        print("\n5. WITHOUT TIMESTAMPS")
        print("   Only the Scenario index control should be displayed")
        print("   Subtitle: Optional scenario-based investigation")

    print("\n6. EXISTING VISUALISER BEHAVIOUR")
    print("   Select other components and inspect their base attributes")
    print("   Click compatible attribute cells to inspect graphs")
    print("   Verify existing topology interactions still work")
    print("=" * 60)


def main() -> None:
    """Launch the requested F05 manual test configuration."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--timestamps", action="store_true")
    mode.add_argument("--no-timestamps", action="store_true")
    args = parser.parse_args()

    grid, updates, output = build_demo_data()

    print_test_plan(args.timestamps, grid)

    kwargs = {
        "grid": grid,
        "update_data": {ComponentType.line: updates},
        "output_data": {ComponentType.node: output},
        "debug": False,
        "port": 8050,
    }

    if args.timestamps:
        kwargs["timestamps"] = TIMESTAMPS

    visualize(**kwargs)


if __name__ == "__main__":
    main()
