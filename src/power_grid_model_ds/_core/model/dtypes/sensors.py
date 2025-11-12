# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""
Sensor data types
Based on the sensors defined in power grid model:
https://power-grid-model.readthedocs.io/en/v1.9.13/user_manual/components.html#sensor
"""

from typing import Annotated, Literal, TypeVar

import numpy as np
from numpy.typing import NDArray

from power_grid_model_ds._core.model.dtypes.id import Id

# define structural arrays with 3 values for 3-phase variables
# based on https://stackoverflow.com/a/72585748
_DT = TypeVar("_DT", bound=np.generic)
NDArray3 = Annotated[NDArray[_DT], Literal[3]]


class Sensor(Id):
    """Base class for sensor data type"""

    measured_object: NDArray[np.int32]


class GenericPowerSensor(Sensor):
    """Base class for power sensor data type"""

    measured_terminal_type: NDArray[np.int32]


class SymPowerSensor(GenericPowerSensor):
    """SymPowerSensor data type"""

    p_measured: NDArray[np.float64]  # measured active power
    q_measured: NDArray[np.float64]  # measured reactive power
    p_sigma: NDArray[np.float64]  # std of active power
    q_sigma: NDArray[np.float64]  # std of reactive power


class AsymPowerSensor(GenericPowerSensor):
    """AsymPowerSensor data type"""

    p_measured: NDArray3[np.float64]  # measured active power
    q_measured: NDArray3[np.float64]  # measured reactive power
    p_sigma: NDArray3[np.float64]  # std of active power
    q_sigma: NDArray3[np.float64]  # std of reactive power


class GenericVoltageSensor(Sensor):
    """Base class for voltage sensor data type"""


class SymVoltageSensor(GenericVoltageSensor):
    """SymVoltageSensor data type"""

    u_sigma: NDArray[np.float64]  # std of voltage
    u_measured: NDArray[np.float64]  # measured voltage
    u_angle_measured: NDArray[np.float64]  # measured phase


class AsymVoltageSensor(GenericVoltageSensor):
    """AsymVoltageSensor data type"""

    u_sigma: NDArray3[np.float64]  # std of 3 voltages
    u_measured: NDArray3[np.float64]  # measured 3 voltages
    u_angle_measured: NDArray3[np.float64]  # measured 3 phases


class GenericCurrentSensor(Sensor):
    """Base class for current sensor data type"""

    measured_terminal_type: NDArray[np.int32]
    angle_measurement_type: NDArray[np.int32]
    i_sigma: NDArray[np.float64]
    i_angle_sigma: NDArray[np.float64]


class SymCurrentSensor(GenericCurrentSensor):
    """SymCurrentSensor data type"""

    i_measured: NDArray[np.float64]
    i_angle_measured: NDArray[np.float64]


class AsymCurrentSensor(GenericCurrentSensor):
    """AsymCurrentSensor data type"""

    i_measured: NDArray3[np.float64]
    i_angle_measured: NDArray3[np.float64]
