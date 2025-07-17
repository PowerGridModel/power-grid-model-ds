# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest
from power_grid_model import BranchSide, LoadGenType, WindingType

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import (
    LineArray,
    LinkArray,
    NodeArray,
    SourceArray,
    SymLoadArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
)


@pytest.fixture
def simple_loadflow_grid(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(2)
    nodes.id = [0, 1]
    nodes.u_rated = [10_500] * 2

    lines = LineArray.zeros(1)
    lines.id = [2]
    lines.from_node = [0]
    lines.to_node = [1]
    lines.from_status = [1]
    lines.to_status = [1]
    lines.r1 = [0.1]
    lines.x1 = [0.01]

    sources = SourceArray.zeros(1)
    sources.id = [3]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    loads = SymLoadArray.zeros(1)
    loads.id = [4]
    loads.node = [1]
    loads.status = [1]
    loads.type = [LoadGenType.const_power]
    loads.p_specified = [250_000]
    loads.q_specified = [50_000]

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    return grid


@pytest.fixture
def loadflow_grid_with_transformer(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(3)
    nodes.id = [0, 1, 2]
    nodes.u_rated = [10_500] * 2 + [3_000]

    lines = LineArray.zeros(1)
    lines.id = 3
    lines.from_node = 0
    lines.to_node = 1
    lines.from_status = 1
    lines.to_status = 1
    lines.r1 = 0.1
    lines.x1 = 0.01

    sources = SourceArray.zeros(1)
    sources.id = 4
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(2)
    loads.id = [5, 6]
    loads.node = [1, 2]
    loads.status = [1, 1]
    loads.p_specified = [25_000] * 2
    loads.q_specified = [5_000] * 2

    transformers = TransformerArray(
        id=[7],
        from_node=[1],
        to_node=[2],
        from_status=[1],
        to_status=[1],
        u1=[10_500],
        u2=[3_000],
        sn=[30e6],
        clock=[12],
        tap_size=[2.5e3],
        uk=[0.203],
        pk=[100e3],
        i0=[0.0],
        p0=[0.0],
        winding_from=[WindingType.wye.value],
        winding_to=[WindingType.wye.value],
        tap_side=[BranchSide.from_side.value],
        tap_pos=[0],
        tap_min=[-11],
        tap_max=[9],
        tap_nom=[0],
    )

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    grid.append(transformers)

    return grid


@pytest.fixture
def grid_with_three_winding_transformer(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(3)
    nodes.id = [0, 1, 2]
    nodes.u_rated = [150_000, 20_000, 10_000]

    sources = SourceArray.zeros(1)
    sources.id = 4
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(2)
    loads.id = [5, 6]
    loads.node = [1, 2]
    loads.status = [1, 1]
    loads.p_specified = [25_000] * 2
    loads.q_specified = [5_000] * 2

    three_winding_transformer = ThreeWindingTransformerArray.empty(1)
    three_winding_transformer.id = [7]
    three_winding_transformer.node_1 = [0]
    three_winding_transformer.node_2 = [1]
    three_winding_transformer.node_3 = [2]
    three_winding_transformer.status_1 = [1]
    three_winding_transformer.status_2 = [1]
    three_winding_transformer.status_3 = [1]
    three_winding_transformer.u1 = [150_000]
    three_winding_transformer.u2 = [20_000]
    three_winding_transformer.u3 = [10_000]
    three_winding_transformer.sn_1 = [1e5]
    three_winding_transformer.sn_2 = [1e5]
    three_winding_transformer.sn_3 = [1e5]
    three_winding_transformer.uk_12 = [0.09]
    three_winding_transformer.uk_13 = [0.06]
    three_winding_transformer.uk_23 = [0.06]
    three_winding_transformer.pk_12 = [1e3]
    three_winding_transformer.pk_13 = [1e3]
    three_winding_transformer.pk_23 = [1e3]
    three_winding_transformer.i0 = [0]
    three_winding_transformer.p0 = [0]
    three_winding_transformer.winding_1 = [2]
    three_winding_transformer.winding_2 = [1]
    three_winding_transformer.winding_3 = [1]
    three_winding_transformer.clock_12 = [5]
    three_winding_transformer.clock_13 = [5]
    three_winding_transformer.tap_side = [0]
    three_winding_transformer.tap_pos = [0]
    three_winding_transformer.tap_min = [-10]
    three_winding_transformer.tap_max = [10]
    three_winding_transformer.tap_nom = [0]
    three_winding_transformer.tap_size = [1380]

    grid.append(nodes)
    grid.append(sources)
    grid.append(loads)
    grid.append(three_winding_transformer)
    return grid


@pytest.fixture
def grid_with_link(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(2)
    nodes.id = [0, 1]
    nodes.u_rated = [10_500] * 2

    lines = LinkArray.zeros(1)
    lines.id = 2
    lines.from_node = 0
    lines.to_node = 1
    lines.from_status = 1
    lines.to_status = 1

    sources = SourceArray.zeros(1)
    sources.id = 3
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(1)
    loads.id = 4
    loads.node = 1
    loads.status = 1
    loads.type = [LoadGenType.const_power]
    loads.p_specified = [250_000]
    loads.q_specified = [50_000]

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    return grid


@pytest.fixture
def grid_with_tap_regulator(grid: Grid) -> Grid:
    """
    Network:
                        (tap_side)  (control side)
    source_1 --- node_2 --- transformer_5 --- node_3 --- line_6 --- node_4 --- load_7
                            |                    |
            transformer_tap_regulator_8 <--------/ (control voltage)
    """
    # source
    sources = SourceArray.zeros(1)
    sources.id = [1]
    sources.node = [2]
    sources.status = [1]
    sources.u_ref = [1.0]
    grid.append(sources)

    # node
    nodes = NodeArray.zeros(3)
    nodes.id = [2, 3, 4]
    nodes.u_rated = [1e4, 4e2, 4e2]
    grid.append(nodes)

    # transformer
    transformers = TransformerArray.zeros(1)
    transformers.id = [5]
    transformers.from_node = [2]
    transformers.to_node = [3]
    transformers.from_status = [1]
    transformers.to_status = [1]
    transformers.u1 = [1e4]
    transformers.u2 = [4e2]
    transformers.sn = [1e5]
    transformers.uk = [0.1]
    transformers.pk = [1e3]
    transformers.i0 = [1.0e-6]
    transformers.p0 = [0.1]
    transformers.winding_from = [2]
    transformers.winding_to = [1]
    transformers.clock = [5]
    transformers.tap_side = [0]
    transformers.tap_pos = [3]
    transformers.tap_min = [-11]
    transformers.tap_max = [9]
    transformers.tap_size = [100]
    grid.append(transformers)

    # line
    lines = LineArray.zeros(1)
    lines.id = [6]
    lines.from_node = [3]
    lines.to_node = [4]
    lines.from_status = [1]
    lines.to_status = [1]
    lines.r1 = [10.0]
    lines.x1 = [0.0]
    lines.c1 = [0.0]
    lines.tan1 = [0.0]
    grid.append(lines)

    # load
    sym_loads = SymLoadArray.zeros(1)
    sym_loads.id = [7]
    sym_loads.node = [4]
    sym_loads.status = [1]
    sym_loads.type = [LoadGenType.const_power]
    sym_loads.p_specified = [1e3]
    sym_loads.q_specified = [5e3]
    grid.append(sym_loads)

    # transformer tap regulator
    transformer_tap_regulators = TransformerTapRegulatorArray.zeros(1)
    transformer_tap_regulators.id = [8]
    transformer_tap_regulators.regulated_object = [5]
    transformer_tap_regulators.status = [1]
    transformer_tap_regulators.control_side = [BranchSide.to_side.value]
    transformer_tap_regulators.u_set = [400.0]
    transformer_tap_regulators.u_band = [20.0]
    transformer_tap_regulators.line_drop_compensation_r = [0.0]
    transformer_tap_regulators.line_drop_compensation_x = [0.0]
    grid.append(transformer_tap_regulators)
    return grid
