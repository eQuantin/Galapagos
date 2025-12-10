from models.Neo4j.islands import get_island_by_port
from models.Neo4j.lockers import get_locker_by_port
from models.Neo4j.ports import (
    get_all_ports,
    get_nearby_ports,
    get_port,
    get_shortest_path_between_ports,
)
from models.Neo4j.seaplanes import get_seaplanes_by_port
from models.Neo4j.warehouse import get_warehouse_by_port


def resolve_ports(obj, info):
    return get_all_ports()


def resolve_port(obj, info, name):
    return get_port(name)


def resolve_port_island(obj, info):
    port = obj.get("name")
    if port:
        return get_island_by_port(port)
    return None


def resolve_port_locker(obj, info):
    port = obj.get("name")
    if port:
        return get_locker_by_port(port)
    return None


def resolve_port_warehouse(obj, info):
    port = obj.get("name")
    if port:
        return get_warehouse_by_port(port)
    return None


def resolve_port_seaplanes(obj, info):
    port = obj.get("name")
    if port:
        return get_seaplanes_by_port(port)
    return None


def resolve_nearby_ports(obj, info, portName, maxDistanceKm=None, limit=None):
    """
    Resolve nearby ports query.
    Returns a list of ports with their distances from the specified port.
    """
    return get_nearby_ports(portName, max_distance_km=maxDistanceKm, limit=limit)


def resolve_shortest_path_between_ports(obj, info, startPort, endPort):
    """
    Resolve shortest path between two ports query.
    Returns the shortest path using Dijkstra's algorithm based on distance weights.
    """
    return get_shortest_path_between_ports(startPort, endPort)
