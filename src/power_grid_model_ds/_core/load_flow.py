# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Power flow functions and classes"""

import warnings
from typing import Dict, Optional

import numpy as np
from numpy.typing import NDArray
from power_grid_model import CalculationMethod, PowerGridModel, initialize_array

from power_grid_model_ds._core.model.grids.base import Grid

PGM_ARRAYS = [
    "node",
    "line",
    "link",
    "transformer",
    "three_winding_transformer",
    "sym_load",
    "sym_gen",
    "source",
    "transformer_tap_regulator",
    "sym_power_sensor",
    "sym_voltage_sensor",
    "asym_voltage_sensor",
]


class PGMCoreException(Exception):
    """Raised when there is an error in running the power grid model"""


class PowerGridModelInterface:
    """Interface between the Grid and the PowerGridModel (pgm).

    - Can convert grid data to pgm input
    - Can calculate power flow
    - Can do batch calculations using pgm
    - Can update grid with output from power flow
    """

    def __init__(
        self,
        grid: Optional[Grid] = None,
        input_data: Optional[Dict] = None,
        system_frequency: float = 50.0,
    ):
        self.grid = grid or Grid.empty()
        self.system_frequency = system_frequency

        self._input_data = input_data or {}
        self.output_data: dict[str, NDArray] = {}
        self.model: Optional[PowerGridModel] = None

    @property
    def input_data(self) -> Dict[str, NDArray]:
        """Get the input data for the PowerGridModel."""
        warnings.warn(
            "Input data has been made private and will be removed as public properety in a future version. "
            "Do not use it directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._input_data

    def create_input_from_grid(self):
        """
        Create input for the PowerGridModel
        """
        for array_name in PGM_ARRAYS:
            pgm_array = self._create_power_grid_array(array_name=array_name)
            self._input_data[array_name] = pgm_array
        return self._input_data

    def create_grid_from_input_data(self, check_ids: bool = True) -> Grid:
        """
        Create Grid object from PowerGridModel input.
        Note that for some arrays, not all fields are available in the PowerGridModel input.
        In this case, the default values are used.

        Args:
            check_ids: if True, check if the ids are unique

        Returns a Grid object with the arrays filled with the PowerGridModel input.
        """
        for pgm_name in PGM_ARRAYS:
            if pgm_name in self._input_data:
                pgm_ds_array_class = getattr(self.grid, pgm_name).__class__
                pgm_ds_array = pgm_ds_array_class(self._input_data[pgm_name])
                self.grid.append(pgm_ds_array, check_max_id=False)
        if check_ids:
            self.grid.check_ids()
        return self.grid

    def calculate_power_flow(
        self,
        calculation_method: CalculationMethod = CalculationMethod.newton_raphson,
        update_data: Optional[Dict] = None,
        **kwargs,
    ):
        """Initialize the PowerGridModel and calculate power flow over input data.

        If input data is not available, self.create_input_from_grid() will be called to create it.

        Returns output of the power flow calculation (also stored in self.output_data)
        """
        self.model = self.model or self.setup_model()

        self.output_data = self.model.calculate_power_flow(
            calculation_method=calculation_method, update_data=update_data, **kwargs
        )
        return self.output_data

    def _create_power_grid_array(self, array_name: str) -> np.ndarray:
        """Create power grid model array"""
        internal_array = getattr(self.grid, array_name)
        pgm_array = initialize_array("input", array_name, internal_array.size)
        fields = self._match_dtypes(pgm_array.dtype, internal_array.dtype)
        pgm_array[fields] = internal_array.data[fields]
        return pgm_array

    def update_model(self, update_data: Dict):
        """
        Updates the power-grid-model using update_data, this allows for batch calculations

        Example:
            Example of update_data creation:

            >>> update_sym_load = initialize_array('update', 'sym_load', 2)
            >>> update_sym_load['id'] = [4, 7]  # same ID
            >>> update_sym_load['p_specified'] = [30e6, 15e6]  # change active power
            >>> # leave reactive power the same, no need to specify
            >>>
            >>> update_line = initialize_array('update', 'line', 1)
            >>> update_line['id'] = [3]  # change line ID 3
            >>> update_line['from_status'] = [0]  # switch off at from side
            >>> # leave to-side swichint status the same, no need to specify
            >>>
            >>> update_data = {
            >>>    'sym_load': update_sym_load,
            >>>    'line': update_line
            >>> }


        """
        self.model = self.model or self.setup_model()
        self.model.update(update_data=update_data)

    def update_grid(self) -> None:
        """
        Fills the output values in the grid for the values that are present
        """
        if not self.output_data:
            raise PGMCoreException("Can not update grid without output_data")
        for array_name in PGM_ARRAYS:
            if array_name in self.output_data.keys():
                internal_array = getattr(self.grid, array_name)
                pgm_output_array = self.output_data[array_name]
                fields = self._match_dtypes(pgm_output_array.dtype, internal_array.dtype)
                internal_array[fields] = pgm_output_array[fields]

    @staticmethod
    def _match_dtypes(first_dtype: np.dtype, second_dtype: np.dtype):
        return list(set(first_dtype.names).intersection(set(second_dtype.names)))  # type: ignore[arg-type]

    def setup_model(self):
        """Setup the PowerGridModel with the input data."""
        self._input_data = self._input_data or self.create_input_from_grid()
        self.model = PowerGridModel(self._input_data, system_frequency=self.system_frequency)
        return self.model
