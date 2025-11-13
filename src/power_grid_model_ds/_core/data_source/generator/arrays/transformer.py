# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generator for LineArray"""

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.base import BaseGenerator
from power_grid_model_ds._core.model.arrays import TransformerArray


class TransformerGenerator(BaseGenerator):
    """Generator for tranformer elements in the grid"""

    def run(self, amount: int) -> TransformerArray:
        """Generate transformers"""

        # Create transformers from 10kV to 3kV
        from_mask = self.grid.node["u_rated"] == 10_500
        from_nodes = self.rng.choice(self.grid.node["id"][from_mask], amount, replace=True)
        to_mask = self.grid.node["u_rated"] == 3_000
        to_nodes = self.rng.choice(self.grid.node["id"][to_mask], amount, replace=False)
        transformer_array = self.grid.transformer.__class__.zeros(amount)
        transformer_array["id"] = 1 + self.grid.max_id + np.arange(amount)
        transformer_array["from_node"] = from_nodes
        transformer_array["to_node"] = to_nodes
        transformer_array["from_status"] = [1] * amount
        transformer_array["to_status"] = [1] * amount
        transformer_array["u1"] = [10_500] * amount
        transformer_array["u2"] = [3_000] * amount
        transformer_array["sn"] = [30e6] * amount
        transformer_array["clock"] = [12] * amount
        transformer_array["uk"] = [0.203] * amount
        transformer_array["pk"] = [100e3] * amount

        return transformer_array
