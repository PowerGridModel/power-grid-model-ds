<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

The Grid
=============

Power Grid Model DS offers a comprehensive solution for managing and maintaining the consistency of entire grid models. This tool facilitates straightforward modifications, extensive analysis, and the enhancement of the Power-Grid-Model data structure by incorporating analysis-specific attributes. At the core of this system is the ``Grid`` class, designed to serve as the foundation for all operations.

Power Grid Model DS supports two primary representations: an array representation and a graph representation. The array representation simplifies the definition process, enables seamless integration with the power-grid-model, and supports comprehensive analysis across the grid. On the other hand, the graph representation excels in exploring the grid's structure, allowing users to easily identify paths and connected components. This dual-representation approach ensures flexibility and adaptability for a wide range of analytical needs.

Array Container
----------------------------------

The array container houses all the arrays for the different components in the ``Grid``. This datamodel is similar to the power-grid-model representation and is described on their documentation: [data-model](https://github.com/PowerGridModel/power-grid-model/blob/main/docs/user_manual/data-model.md) and [components](https://github.com/PowerGridModel/power-grid-model/blob/main/docs/user_manual/components.md). The array types can be extended and class types can be used to recognize which component you are handling.

Graph Container
----------------------------------

The base Grid only has an array representation but it can be extended to a ``Grid``. This contains a ``GraphContainer`` in addition to the ``FancyArray``s. The ``GraphContainer`` has two different graphs which are kept track of, an active graph containing all active branches and a complete graph which contains all branches in the network. In the ``GraphContainer`` the topology is represented as a node-branch model with a rustworkx implementation.

The ``GraphContainer`` has additional functions such as ``get_nearest_substation_node`` and ``get_downstream_nodes``. The underlying ``NetworkGraph`` class also provides specific functions such as ``get_shortest_path``, ``get_all_paths``, ``get_components`` and ``get_connected``.

Network consistency
----------------------------------

To make sure both representations are and stay consistent the ``Grid`` contains functions to modify both representation correctly, such as ``add_node`` or ``make_active``. The ``GraphContainer`` can also be initialized from a complete array representation using the ``from_arrays`` functionality. The API is further described in the model interface section.
