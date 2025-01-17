# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

NUMPY_DTYPE = (
    "dtype = [('id', '<i8'), ('test_int', '<i8'), ('test_float', '<f8'), ('test_str', '<U50'), ('test_bool', '?')]; "
)

SETUP_CODES = {
    "structured": "import numpy as np;" + NUMPY_DTYPE + "input_array = np.zeros({array_size}, dtype=dtype)",
    "rec": "import numpy as np;" + NUMPY_DTYPE + "input_array = np.recarray(({array_size},),dtype=dtype)",
    "fancy": "from tests.conftest import FancyTestArray; input_array=FancyTestArray.zeros({array_size});"
    + "import numpy as np;input_array.id = np.arange({array_size})",
}

GRAPH_SETUP_CODES = {
    "rustworkx": "from power_grid_model_ds.model.grids.base import Grid;"
    + "from power_grid_model_ds.data_source.generator.grid_generators import RadialGridGenerator;"
    + "from power_grid_model_ds.model.graphs.models import RustworkxGraphModel;"
    + "grid=RadialGridGenerator(nr_nodes={graph_size}, grid_class=Grid, graph_model=RustworkxGraphModel).run()",
}

SINGLE_REPEATS = 1000
LOOP_REPEATS = 100
ARRAY_SIZES_SMALL = [1000, 5000]
ARRAY_SIZES_LARGE = [10000, 50000]
