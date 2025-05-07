"""
Definitions:

- Feeder branch: A branch that connects a substation to a distribution network.
- Route: A path of nodes with a single feeder branch.


"""

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import LineArray, NodeArray

# NodeArray.station_name?


class NoCandidateNodesError(Exception):
    """Exception raised when no candidate nodes are found for a new substation."""


def build_new_substation(grid: Grid, location: tuple[float, float]) -> None:
    """Build a new substation at the given location.

    (Create a substation node at the given location)
    """


def get_all_routes(grid: Grid, substation_node: NodeArray) -> list[NodeArray]:
    """Get all routes that originate from a given substation node."""


def transfer_routes(grid: Grid, old_substation: NodeArray, new_substation: NodeArray) -> None:
    """Migrate a subset of the routes of the old substation to the new substation.
    Each route can be migrated fully or partially.

    """
    routes = get_all_routes(grid, old_substation)
    for route in routes:
        try:
            connection_point = find_connection_point(route, old_substation, new_substation)
        except NoCandidateNodesError:
            continue

        connect_to_route(grid, route, new_substation)


def find_connection_point(route: NodeArray, old_substation: NodeArray, new_substation: NodeArray) -> NodeArray:
    """Calculate the connection point for the new route.
    This should be the geographically closest node to the new substation.

    Should raise NoCandidateNodesError if all nodes in the route are geographically closer to the old substation.
    """


def connect_to_route(grid: Grid, connection_point: NodeArray, new_substation: NodeArray) -> None:
    """Connect the new substation node to the connection point.

    1. Create a new line that connects the two nodes
    2. Deactivate the line that connects the connection point to the old substation
    """


def optimize_route_transfer(grid: Grid, connection_point: NodeArray) -> None:
    """Attempt to optimize the route transfer moving the naturally open point (NOP) upstream towards the old substation.
    This way, the new substation will take over more nodes of the original route.

    Note that a node cannot be taken over if that results in a capacity issue on the grid.
    """


def check_for_capacity_issues(grid: Grid) -> tuple[NodeArray, LineArray]:
    """Check for capacity issues on the grid.
    Return the nodes and lines that with capacity issues.
    """
