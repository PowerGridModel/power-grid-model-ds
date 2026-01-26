# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""helpers for grid tests"""

from typing import TypeVar

from power_grid_model_ds._core.model.arrays import (
    LineArray,
    NodeArray,
    SourceArray,
    SymLoadArray,
    ThreeWindingTransformerArray,
)
from power_grid_model_ds._core.model.enums.nodes import NodeType
from power_grid_model_ds._core.model.grids.base import Grid

T = TypeVar("T", bound=Grid)


def build_basic_grid(grid: T) -> T:
    """Build a basic grid"""

    # This defines a circle with 4 medium voltage stations and a 400V rail (12)

    # Legend:
    #     Node: ***  (ids: 1xx)
    #     Line: ---  (ids: 2xx)
    #     Transformer: {-}  (ids: 3xx)
    #     Link: {-}  (ids: 6xx)
    #     Power gap: -|-

    # Nodes Topology
    # (SUBSTATION) 101 --- 102 --- 103 -|- 104 --- 105 --- 101 (SUBSTATION)
    #                      {-}
    #                      106

    # Branches Topology:
    # (SUBSTATION) *** 201 *** 202 *** 203 *** 601 *** 204 *** (SUBSTATION)
    #                      301
    #                      ***

    # Add Substations
    substation = grid.node.__class__(id=[101], u_rated=[10_500.0], node_type=[NodeType.SUBSTATION_NODE.value])
    grid.append(substation, check_max_id=False)

    # Add Nodes
    nodes = grid.node.__class__(
        id=[102, 103, 104, 105, 106],
        u_rated=[10_500.0] * 4 + [400.0],
    )
    grid.append(nodes, check_max_id=False)

    # Add Lines
    lines = grid.line.__class__(
        id=[201, 202, 203, 204],
        from_status=[1, 1, 0, 1],
        to_status=[1, 1, 0, 1],
        from_node=[101, 102, 103, 101],
        to_node=[102, 103, 104, 105],
        i_n=[200.0] * 4,
        r1=[0.1] * 4,
        x1=[0.03] * 4,
        c1=[0.0] * 4,
        tan1=[0.0] * 4,
    )
    grid.append(lines, check_max_id=False)

    # Add a transformer
    transformer = grid.transformer.__class__.empty(1)
    transformer.id = 301
    transformer.from_status = 1
    transformer.to_status = 1
    transformer.from_node = 102
    transformer.to_node = 106

    grid.append(transformer, check_max_id=False)

    # Add a link
    link = grid.link.__class__.empty(1)
    link.id = 601
    link.from_status = 1
    link.to_status = 1
    link.from_node = 104
    link.to_node = 105

    grid.append(link, check_max_id=False)

    # Loads
    loads = grid.sym_load.__class__(
        id=[401, 402, 403, 404],
        node=[102, 103, 104, 105],
        type=[1] * 4,
        p_specified=[1_000_000.0] * 4,
        q_specified=[1_000_000.0] * 4,
        status=[1] * 4,
    )
    grid.append(loads, check_max_id=False)

    # Add Source
    source = grid.source.__class__(id=[501], node=[101], status=[1], u_ref=[0.0])
    grid.append(source, check_max_id=False)
    grid.check_ids()

    return grid


def build_basic_grid_with_three_winding(grid: T) -> T:
    """Build a grid with three winding transformer"""

    # This defines a network being fed from a single 150kV node through a three winding transformer
    # creating a 10kV and 20kV route to the network.

    # Legend:
    #     Node: ***  (ids: 1xx)
    #     Line: ---  (ids: 2xx)
    #     Transformer: {-}  (ids: 3xx)
    #     Link: {-}  (ids: 6xx)
    #     Power gap: -|-

    # Nodes Topology
    # (SUBSTATION) 101            /102 --- 104 -|- 105 --- 106 --- 102 (SUBSTATION)
    #                 \{3 winding}
    #                             \103 --- 107 -|- 108 --- 109 --- 103 (SUBSTATION)

    # Branches Topology:
    # (SUBSTATION) ***           /*** 201 *** 202 *** 203 *** 204 *** (SUBSTATION)
    #                 \{  301  }
    #                            \*** 205 *** 206 *** 207 *** 208 *** (SUBSTATION)

    # Add Nodes
    nodes = NodeArray(
        id=[104, 105, 106, 107, 108, 109],
        u_rated=[10_500.0] * 6,
    )
    grid.append(nodes, check_max_id=False)

    # Add Substations
    substation = NodeArray(
        id=[101, 102, 103],
        u_rated=[150_000, 20_000, 10_000],
        node_type=[NodeType.SUBSTATION_NODE.value] * 3,
    )
    grid.append(substation, check_max_id=False)

    # Add Lines
    lines = LineArray(
        id=[201, 202, 203, 204, 205, 206, 207, 208],
        from_status=[1, 1, 1, 1, 1, 1, 1, 1],
        to_status=[1, 0, 1, 1, 1, 0, 1, 1],
        from_node=[102, 104, 106, 102, 103, 107, 109, 103],
        to_node=[104, 105, 105, 106, 107, 108, 108, 109],
        i_n=[200.0] * 8,
        r1=[0.1] * 8,
        x1=[0.03] * 8,
        c1=[0.0] * 8,
        tan1=[0.0] * 8,
    )
    grid.append(lines, check_max_id=False)

    # Add a transformer
    three_winding_transformer = ThreeWindingTransformerArray.empty(1)
    three_winding_transformer.id = [301]
    three_winding_transformer.node_1 = [101]
    three_winding_transformer.node_2 = [102]
    three_winding_transformer.node_3 = [103]
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

    grid.append(three_winding_transformer, check_max_id=False)

    # Loads
    loads = SymLoadArray(
        id=[401, 402, 403, 404, 405, 406],
        node=[104, 105, 106, 107, 108, 109],
        type=[1] * 6,
        p_specified=[1_000_000.0] * 6,
        q_specified=[1_000_000.0] * 6,
        status=[1] * 6,
    )
    grid.append(loads, check_max_id=False)

    # Add Source
    source = SourceArray(id=[501], node=[101], status=[1], u_ref=[0.0])
    grid.append(source, check_max_id=False)
    grid.check_ids()

    return grid
