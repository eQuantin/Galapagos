from models.Neo4j.islands import get_island_by_port
from models.Neo4j.lockers import get_locker_by_port
from models.Neo4j.ports import (
    get_all_ports,
    get_port,
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
