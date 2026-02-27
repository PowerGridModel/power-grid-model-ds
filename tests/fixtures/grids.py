# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""helpers for grid tests"""

from typing import TypeVar

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
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


def build_topologically_full_grid(grid: T) -> T:
    """Build two disjoint grids with comprehensive component coverage

    Creates two independent (disjoint) grids within a single Grid object, each with a central
    node connected to various components demonstrating all available component types.

    Component Coverage per Grid:
        - Branches: Line, Link, AsymLine, GenericBranch, Transformer, ThreeWindingTransformer
        - Appliances: Source, Shunt, SymLoad, SymGen, AsymLoad, AsymGen, Fault
        - Sensors: SymPowerSensor, AsymPowerSensor, SymCurrentSensor, AsymCurrentSensor,
                   SymVoltageSensor, AsymVoltageSensor
        - Regulators: VoltageRegulator, TransformerTapRegulator

    ID Naming Convention:
        Grid 1: 1xxxx series, Grid 2: 2xxxx series

        Breakdown by component category:
        - Nodes:                  1001-1008, 2001-2008
        - Branches:               10001-10006, 20001-20006
        - Appliances:             11001-11007, 21001-21007
        - Sensors:                12001-12040, 22001-22040
            * Voltage Sensors:        12001-12002, 22001-22002
            * Sym Power Sensors:      12003-12015, 22003-22015 (branches, appliances, loads, gens, central node)
            * Asym Power Sensors:     12016-12028, 22016-22028 (branches, appliances, loads, gens, central node)
            * Sym Current Sensors:    12029-12034, 22029-22034
            * Asym Current Sensors:   12035-12040, 22035-22040
        - Regulators:             13001-13006, 23001-23006
            * Voltage Regulators:     13001-13004, 23001-23004
            * Tap Regulators:         13005-13006, 23005-23006
    """

    # Nodes: 8 per grid (1 central + 7 for branch connections)
    nodes = grid.node.__class__.zeros(16)
    nodes["id"] = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
    grid.append(nodes, check_max_id=False)

    # Lines: central node to secondary node with sensors
    lines = grid.line.__class__.zeros(2)
    lines["id"] = [10001, 20001]
    lines["from_node"] = [1001, 2001]
    lines["to_node"] = [1002, 2002]
    grid.append(lines, check_max_id=False)

    # Links
    links = grid.link.__class__.zeros(2)
    links["id"] = [10002, 20002]
    links["from_node"] = [1001, 2001]
    links["to_node"] = [1003, 2003]
    grid.append(links, check_max_id=False)

    # AsymLines
    asym_lines = grid.asym_line.__class__.zeros(2)
    asym_lines["id"] = [10003, 20003]
    asym_lines["from_node"] = [1001, 2001]
    asym_lines["to_node"] = [1004, 2004]
    grid.append(asym_lines, check_max_id=False)

    # GenericBranches
    generic_branches = grid.generic_branch.__class__.zeros(2)
    generic_branches["id"] = [10004, 20004]
    generic_branches["from_node"] = [1001, 2001]
    generic_branches["to_node"] = [1005, 2005]
    grid.append(generic_branches, check_max_id=False)

    # Transformers with tap regulators
    transformers = grid.transformer.__class__.zeros(2)
    transformers["id"] = [10005, 20005]
    transformers["from_node"] = [1001, 2001]
    transformers["to_node"] = [1006, 2006]
    grid.append(transformers, check_max_id=False)

    # ThreeWindingTransformers with tap regulators
    three_winding = grid.three_winding_transformer.__class__.zeros(2)
    three_winding["id"] = [10006, 20006]
    three_winding["node_1"] = [1001, 2001]
    three_winding["node_2"] = [1007, 2007]
    three_winding["node_3"] = [1008, 2008]
    grid.append(three_winding, check_max_id=False)

    # Sources with power sensors
    sources = grid.source.__class__.zeros(2)
    sources["id"] = [11001, 21001]
    sources["node"] = [1001, 2001]
    grid.append(sources, check_max_id=False)

    # Shunts with power sensors
    shunts = grid.shunt.__class__.zeros(2)
    shunts["id"] = [11002, 21002]
    shunts["node"] = [1001, 2001]
    grid.append(shunts, check_max_id=False)

    # SymLoads with power sensors and voltage regulators
    sym_loads = grid.sym_load.__class__.zeros(2)
    sym_loads["id"] = [11003, 21003]
    sym_loads["node"] = [1001, 2001]
    grid.append(sym_loads, check_max_id=False)

    # SymGens with power sensors and voltage regulators
    sym_gens = grid.sym_gen.__class__.zeros(2)
    sym_gens["id"] = [11004, 21004]
    sym_gens["node"] = [1001, 2001]
    grid.append(sym_gens, check_max_id=False)

    # AsymLoads with power sensors and voltage regulators
    asym_loads = grid.asym_load.__class__.zeros(2)
    asym_loads["id"] = [11005, 21005]
    asym_loads["node"] = [1001, 2001]
    grid.append(asym_loads, check_max_id=False)

    # AsymGens with power sensors and voltage regulators
    asym_gens = grid.asym_gen.__class__.zeros(2)
    asym_gens["id"] = [11006, 21006]
    asym_gens["node"] = [1001, 2001]
    grid.append(asym_gens, check_max_id=False)

    # Faults
    faults = grid.fault.__class__.zeros(2)
    faults["id"] = [11007, 21007]
    faults["fault_object"] = [1001, 2001]
    grid.append(faults, check_max_id=False)

    # Sym Voltage Sensors
    sym_voltage_sensors = grid.sym_voltage_sensor.__class__.zeros(2)
    sym_voltage_sensors["id"] = [12001, 22001]
    sym_voltage_sensors["measured_object"] = [1001, 2001]
    grid.append(sym_voltage_sensors, check_max_id=False)

    # Asym Voltage Sensors
    asym_voltage_sensors = grid.asym_voltage_sensor.__class__.zeros(2)
    asym_voltage_sensors["id"] = [12002, 22002]
    asym_voltage_sensors["measured_object"] = [1001, 2001]
    grid.append(asym_voltage_sensors, check_max_id=False)

    # Sym Power Sensors for branches, appliances, loads, gens, and central nodes
    # (6 branches + source + shunt + 4 loads/gens + 1 central node per grid)
    sym_power_sensors = grid.sym_power_sensor.__class__.zeros(26)
    id_measured_objects = [
        (12003, 1001),
        (12004, 10001),
        (12005, 10002),
        (12006, 10003),
        (12007, 10004),
        (12008, 10005),
        (12009, 10006),
        (12010, 11001),
        (12011, 11002),
        (12012, 11003),
        (12013, 11004),
        (12014, 11005),
        (12015, 11006),
        (22003, 2001),
        (22004, 20001),
        (22005, 20002),
        (22006, 20003),
        (22007, 20004),
        (22008, 20005),
        (22009, 20006),
        (22010, 21001),
        (22011, 21002),
        (22012, 21003),
        (22013, 21004),
        (22014, 21005),
        (22015, 21006),
    ]
    sym_power_sensors["id"] = [id for id, _ in id_measured_objects]
    sym_power_sensors["measured_object"] = [meas for _, meas in id_measured_objects]
    grid.append(sym_power_sensors, check_max_id=False)

    # Asym Power Sensors for branches, appliances, loads, gens, and central nodes
    asym_power_sensors = grid.asym_power_sensor.__class__.zeros(26)
    id_measured_objects = [
        (12016, 1001),
        (12017, 10001),
        (12018, 10002),
        (12019, 10003),
        (12020, 10004),
        (12021, 10005),
        (12022, 10006),
        (12023, 11001),
        (12024, 11002),
        (12025, 11003),
        (12026, 11004),
        (12027, 11005),
        (12028, 11006),
        (22016, 2001),
        (22017, 20001),
        (22018, 20002),
        (22019, 20003),
        (22020, 20004),
        (22021, 20005),
        (22022, 20006),
        (22023, 21001),
        (22024, 21002),
        (22025, 21003),
        (22026, 21004),
        (22027, 21005),
        (22028, 21006),
    ]
    asym_power_sensors["id"] = [id for id, _ in id_measured_objects]
    asym_power_sensors["measured_object"] = [meas for _, meas in id_measured_objects]
    grid.append(asym_power_sensors, check_max_id=False)

    # Sym Current Sensors for branches
    sym_current_sensors = grid.sym_current_sensor.__class__.zeros(12)
    id_measured_objects = [
        (12029, 10001),
        (12030, 10002),
        (12031, 10003),
        (12032, 10004),
        (12033, 10005),
        (12034, 10006),
        (22029, 20001),
        (22030, 20002),
        (22031, 20003),
        (22032, 20004),
        (22033, 20005),
        (22034, 20006),
    ]
    sym_current_sensors["id"] = [id for id, _ in id_measured_objects]
    sym_current_sensors["measured_object"] = [meas for _, meas in id_measured_objects]
    grid.append(sym_current_sensors, check_max_id=False)

    # Asym Current Sensors for branches
    asym_current_sensors = grid.asym_current_sensor.__class__.zeros(12)
    id_measured_objects = [
        (12035, 10001),
        (12036, 10002),
        (12037, 10003),
        (12038, 10004),
        (12039, 10005),
        (12040, 10006),
        (22035, 20001),
        (22036, 20002),
        (22037, 20003),
        (22038, 20004),
        (22039, 20005),
        (22040, 20006),
    ]
    asym_current_sensors["id"] = [id for id, _ in id_measured_objects]
    asym_current_sensors["measured_object"] = [meas for _, meas in id_measured_objects]
    grid.append(asym_current_sensors, check_max_id=False)

    # Voltage Regulators for loads and generators (4 per grid)
    voltage_regulators = grid.voltage_regulator.__class__.zeros(8)
    voltage_regulators["id"] = [13001, 13002, 13003, 13004, 23001, 23002, 23003, 23004]
    voltage_regulators["regulated_object"] = [11003, 11004, 11005, 11006, 21003, 21004, 21005, 21006]
    grid.append(voltage_regulators, check_max_id=False)

    # Transformer Tap Regulators for transformers (2 per grid)
    tap_regulators = grid.transformer_tap_regulator.__class__.zeros(4)
    tap_regulators["id"] = [13005, 13006, 23005, 23006]
    tap_regulators["regulated_object"] = [10005, 10006, 20005, 20006]
    grid.append(tap_regulators, check_max_id=False)

    grid.check_ids()

    return grid
