# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest
from numpy.typing import NDArray
from power_grid_model import ComponentType, MeasuredTerminalType

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    Branch3Array,
    FaultArray,
    LineArray,
    NodeArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    ThreeWindingTransformerArray,
    TransformerTapRegulatorArray,
    VoltageRegulatorArray,
)
from power_grid_model_ds._core.visualizer.parsers import (
    _parse_appliances,
    _parse_faults,
    _parse_flow_sensors,
    _parse_transformer_tap_regulators,
    _parse_voltage_regulators,
    _parse_voltage_sensors,
    parse_branch3_array,
    parse_branch_array,
    parse_node_array,
)
from power_grid_model_ds._core.visualizer.parsing_utils import PGM_ID_KEY
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass
from power_grid_model_ds._core.visualizer.typing import VizToComponentElements


class CoordinatedNodeArray(NodeArray):
    x: NDArray[np.float64]
    y: NDArray[np.float64]


def _fill_expected_with_defaults(array, expected_elements):
    for element in expected_elements:
        for col in array.columns:
            if col not in expected_elements[element]["data"]:
                expected_elements[element]["data"][col] = array[0][col].item()
    return expected_elements


@pytest.fixture
def node_array() -> tuple[NodeArray, VizToComponentElements]:
    nodes = NodeArray.zeros(4)
    nodes[:] = 99
    nodes["id"] = [1, 2, 3, 4]
    nodes["u_rated"] = [100.0, 200.0, 300.0, 400.0]

    expected_elements: VizToComponentElements = {
        str(nodes["id"][i]): {
            "data": {
                "id": str(nodes["id"][i]),
                PGM_ID_KEY: nodes["id"][i].item(),
                "group": "node",
                "u_rated": nodes["u_rated"][i].item(),
                "associated_ids": {ComponentType.node.value: [nodes["id"][i].item()]},
            },
            "classes": f"{StyleClass.NODE.value}",
        }
        for i in range(4)
    }
    _fill_expected_with_defaults(nodes, expected_elements)

    return nodes, expected_elements


@pytest.fixture
def node_array_with_coordinates() -> tuple[CoordinatedNodeArray, VizToComponentElements]:
    nodes = CoordinatedNodeArray.zeros(4)
    nodes[:] = 99
    nodes["id"] = [1, 2, 3, 4]
    nodes["x"] = [10.0, 20.0, 30.0, 40.0]
    nodes["y"] = [10.0, 20.0, 30.0, 40.0]
    nodes["u_rated"] = [100.0, 200.0, 300.0, 400.0]

    expected_elements: VizToComponentElements = {
        str(nodes["id"][i]): {
            "data": {
                "id": str(nodes["id"][i]),
                PGM_ID_KEY: nodes["id"][i].item(),
                "group": "node",
                "u_rated": nodes["u_rated"][i].item(),
                "x": nodes["x"][i].item(),
                "y": nodes["y"][i].item(),
                "associated_ids": {ComponentType.node.value: [nodes["id"][i].item()]},
            },
            "position": {
                "x": nodes["x"][i].item(),
                "y": -nodes["y"][i].item(),
            },
            "classes": f"{StyleClass.NODE.value}",
        }
        for i in range(4)
    }
    _fill_expected_with_defaults(nodes, expected_elements)

    return nodes, expected_elements


@pytest.fixture
def line_array() -> tuple[LineArray, VizToComponentElements]:
    lines = LineArray.zeros(3)
    lines[:] = 99
    lines["id"] = [100, 101, 102]
    lines["from_node"] = [1, 2, 3]
    lines["to_node"] = [4, 5, 6]

    expected_elements: VizToComponentElements = {
        str(lines["id"][i]): {
            "data": {
                "id": str(lines["id"][i]),
                PGM_ID_KEY: lines["id"][i].item(),
                "group": "line",
                "source": str(lines["from_node"][i]),
                "target": str(lines["to_node"][i]),
                "from_node": lines["from_node"][i].item(),
                "to_node": lines["to_node"][i].item(),
                "associated_ids": {
                    ComponentType.line.value: [lines["id"][i].item()],
                },
            },
            "classes": f"{StyleClass.BRANCH.value}",
        }
        for i in range(3)
    }
    _fill_expected_with_defaults(lines, expected_elements)

    return lines, expected_elements


@pytest.fixture
def branch3_array() -> tuple[Branch3Array, VizToComponentElements]:
    branch3 = ThreeWindingTransformerArray.zeros(1)
    branch3[:] = 99
    branch3["id"] = [200]
    branch3["node_1"] = [1]
    branch3["node_2"] = [2]
    branch3["node_3"] = [3]
    branch3["uk_12"] = [0.1]

    expected_elements: VizToComponentElements = {
        "200_0": {
            "data": {
                "id": "200_0",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "1",
                "target": "2",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_1": {
            "data": {
                "id": "200_1",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "1",
                "target": "3",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_2": {
            "data": {
                "id": "200_2",
                PGM_ID_KEY: 200,
                "group": "three_winding_transformer",
                "source": "2",
                "target": "3",
                "node_1": 1,
                "node_2": 2,
                "node_3": 3,
                "uk_12": 0.1,
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
    }
    _fill_expected_with_defaults(branch3, expected_elements)
    return branch3, expected_elements


@pytest.fixture
def appliance_array() -> tuple[SymLoadArray, VizToComponentElements, VizToComponentElements]:
    array = SymLoadArray.zeros(2)
    array[:] = 99
    array["id"] = [100, 101]
    array["node"] = [1]

    starting_elements: VizToComponentElements = {
        "1": {
            "data": {
                "id": "1",
                "group": "node",
                "associated_ids": {ComponentType.node.value: [100, 101]},
            },
            "classes": f"{StyleClass.NODE.value}",
        }
    }

    expected_elements = starting_elements.copy()
    expected_elements.update(
        {
            "100": {
                "data": {
                    "id": "100",
                    "group": "sym_load",
                    "source": "1",
                    "target": "100_ghost_node",
                    "associated_ids": {
                        ComponentType.sym_load.value: [100],
                    },
                },
                "classes": f"{StyleClass.LOADING_APPLIANCE.value}",
            },
            "100_ghost_node": {
                "data": {
                    "id": "100_ghost_node",
                    "group": "sym_load_ghost_node",
                    "associated_ids": {
                        ComponentType.sym_load.value: [100],
                    },
                },
                "classes": f"{StyleClass.APPLIANCE_GHOST_NODE.value}",
                "selectable": False,
            },
            "101": {
                "data": {
                    "id": "101",
                    "group": "sym_load",
                    "source": "1",
                    "target": "101_ghost_node",
                    "associated_ids": {
                        ComponentType.sym_load.value: [101],
                    },
                },
                "classes": f"{StyleClass.LOADING_APPLIANCE.value}",
            },
            "101_ghost_node": {
                "data": {
                    "id": "101_ghost_node",
                    "group": "sym_load_ghost_node",
                    "associated_ids": {
                        ComponentType.sym_load.value: [101],
                    },
                },
                "classes": f"{StyleClass.APPLIANCE_GHOST_NODE.value}",
                "selectable": False,
            },
        }
    )

    return array, starting_elements, expected_elements


@pytest.fixture
def transformer_tap_regulator_array() -> tuple[
    TransformerTapRegulatorArray, VizToComponentElements, VizToComponentElements
]:
    array = TransformerTapRegulatorArray.zeros(2)
    array[:] = 99
    array["id"] = [100, 101]
    array["regulated_object"] = [200, 201]

    starting_elements: VizToComponentElements = {
        "200_0": {
            "data": {
                "id": "200_0",
                "group": "three_winding_transformer",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_1": {
            "data": {
                "id": "200_1",
                "group": "three_winding_transformer",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "200_2": {
            "data": {
                "id": "200_2",
                "group": "three_winding_transformer",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [200],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "201": {
            "data": {
                "id": "201",
                "group": "transformer",
                "associated_ids": {ComponentType.transformer.value: [201]},
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
    }

    expected_elements = starting_elements.copy()
    expected_elements["200_0"]["data"]["associated_ids"].update({ComponentType.transformer_tap_regulator.value: [100]})
    expected_elements["200_1"]["data"]["associated_ids"].update({ComponentType.transformer_tap_regulator.value: [100]})
    expected_elements["200_2"]["data"]["associated_ids"].update({ComponentType.transformer_tap_regulator.value: [100]})
    expected_elements["201"]["data"]["associated_ids"].update({ComponentType.transformer_tap_regulator.value: [101]})

    return array, starting_elements, expected_elements


@pytest.fixture
def voltage_regulator_array() -> tuple[VoltageRegulatorArray, VizToComponentElements, VizToComponentElements]:
    array = VoltageRegulatorArray.zeros(1)
    array[:] = 99
    array["id"] = [100]
    array["regulated_object"] = [200]

    starting_elements: VizToComponentElements = {
        "200": {
            "data": {
                "id": "200",
                "group": "sym_load",
                "associated_ids": {ComponentType.sym_load.value: [200]},
            },
            "classes": f"{StyleClass.LOADING_APPLIANCE.value}",
        }
    }

    expected_elements = starting_elements.copy()
    expected_elements["200"]["data"]["associated_ids"].update({ComponentType.voltage_regulator.value: [100]})

    return array, starting_elements, expected_elements


@pytest.fixture
def voltage_sensor_array() -> tuple[SymVoltageSensorArray, VizToComponentElements, VizToComponentElements]:
    array = SymVoltageSensorArray.zeros(1)
    array[:] = 99
    array["id"] = [100]
    array["measured_object"] = [200]

    starting_elements: VizToComponentElements = {
        "200": {
            "data": {
                "id": "200",
                "group": "node",
                "associated_ids": {ComponentType.node.value: [200]},
            },
            "classes": f"{StyleClass.NODE.value}",
        }
    }

    expected_elements = starting_elements.copy()
    expected_elements["200"]["data"]["associated_ids"].update({ComponentType.sym_voltage_sensor.value: [100]})

    return array, starting_elements, expected_elements


@pytest.fixture
def fault_array() -> tuple[FaultArray, VizToComponentElements, VizToComponentElements]:
    array = FaultArray.zeros(1)
    array[:] = 99
    array["id"] = [100]
    array["fault_object"] = [200]

    starting_elements: VizToComponentElements = {
        "200": {
            "data": {
                "id": "200",
                "group": "node",
                "associated_ids": {ComponentType.node.value: [200]},
            },
            "classes": f"{StyleClass.NODE.value}",
        }
    }

    expected_elements = starting_elements.copy()
    expected_elements["200"]["data"]["associated_ids"].update({ComponentType.fault.value: [100]})

    return array, starting_elements, expected_elements


@pytest.mark.parametrize(
    "func, test_data, kwargs",
    [
        (parse_node_array, "node_array", {}),
        (parse_node_array, "node_array_with_coordinates", {}),
        (parse_branch_array, "line_array", {"group": ComponentType.line}),
        (parse_branch3_array, "branch3_array", {"group": ComponentType.three_winding_transformer}),
    ],
)
def test_parsing(func, request, test_data, kwargs):
    array, expected_elements = request.getfixturevalue(test_data)

    result = func(array, **kwargs)

    assert len(result) == len(expected_elements)
    assert result == expected_elements


@pytest.mark.parametrize(
    "func, test_data, kwargs",
    [
        (_parse_appliances, "appliance_array", {"group": ComponentType.sym_load}),
        (_parse_transformer_tap_regulators, "transformer_tap_regulator_array", {}),
        (_parse_voltage_regulators, "voltage_regulator_array", {}),
        (_parse_voltage_sensors, "voltage_sensor_array", {"group": ComponentType.sym_voltage_sensor}),
        (_parse_faults, "fault_array", {}),
    ],
)
def test_parsing_with_starting_elements(func, request, test_data, kwargs):
    array, starting_elements, expected_elements = request.getfixturevalue(test_data)

    elements = starting_elements.copy()  # to ensure starting_elements is not modified by the function
    func(elements=elements, array=array, **kwargs)

    assert len(elements) == len(expected_elements)
    assert elements == expected_elements


def test_parse_flow_sensors() -> None:
    power_sensors = SymPowerSensorArray.zeros(3)
    power_sensors[:] = 99
    power_sensors["id"] = [1000, 1001, 1002]
    power_sensors["measured_object"] = [100, 101, 102]
    power_sensors["measured_terminal_type"] = [
        MeasuredTerminalType.branch_from,
        MeasuredTerminalType.load,
        MeasuredTerminalType.branch3_1,
    ]

    appliance_to_node = {"101": "1"}
    starting_elements: VizToComponentElements = {
        "1": {
            "data": {
                "id": "1",
                "group": "node",
                "associated_ids": {ComponentType.node.value: [100]},
            },
            "classes": f"{StyleClass.NODE.value}",
        },
        "100": {
            "data": {
                "id": "100",
                "group": "line",
                "associated_ids": {ComponentType.line.value: [100]},
            },
            "classes": f"{StyleClass.LINE.value}",
        },
        "101": {
            "data": {
                "id": "101",
                "group": "sym_load",
                "source": "1",
                "target": "101_ghost_node",
                "associated_ids": {
                    ComponentType.sym_load.value: [101],
                },
            },
            "classes": f"{StyleClass.LOADING_APPLIANCE.value}",
        },
        "102_0": {
            "data": {
                "id": "102_0",
                "group": "three_winding_transformer",
                "source": "99",
                "target": "99",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [102],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "102_1": {
            "data": {
                "id": "102_1",
                "group": "three_winding_transformer",
                "source": "99",
                "target": "99",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [102],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
        "102_2": {
            "data": {
                "id": "102_2",
                "group": "three_winding_transformer",
                "source": "99",
                "target": "99",
                "associated_ids": {
                    ComponentType.three_winding_transformer.value: [102],
                },
            },
            "classes": f"{StyleClass.BRANCH.value} {StyleClass.TRANSFORMER.value}",
        },
    }

    elements = starting_elements.copy()
    _parse_flow_sensors(
        elements=elements,
        array=power_sensors,
        group=ComponentType.sym_power_sensor,
        appliance_to_node=appliance_to_node,
    )

    expected_elements = starting_elements.copy()
    expected_elements["100"]["data"]["associated_ids"].update({ComponentType.sym_power_sensor.value: [1000]})
    expected_elements["1"]["data"]["associated_ids"].update({ComponentType.sym_power_sensor.value: [1001]})
    expected_elements["102_0"]["data"]["associated_ids"].update({ComponentType.sym_power_sensor.value: [1002]})
    expected_elements["102_1"]["data"]["associated_ids"].update({ComponentType.sym_power_sensor.value: [1002]})
    expected_elements["102_2"]["data"]["associated_ids"].update({ComponentType.sym_power_sensor.value: [1002]})

    assert len(elements) == len(expected_elements)
    assert elements == expected_elements


def test_parse_flow_sensors_invalid_measured_terminal_type() -> None:
    power_sensors = SymPowerSensorArray.zeros(1)
    power_sensors["id"] = [1000]
    power_sensors[:] = 99
    power_sensors["measured_terminal_type"] = [1234]

    with pytest.raises(ValueError, match="Unknown measured_terminal_type"):
        _parse_flow_sensors(
            elements={}, array=power_sensors, group=ComponentType.sym_power_sensor, appliance_to_node={}
        )
