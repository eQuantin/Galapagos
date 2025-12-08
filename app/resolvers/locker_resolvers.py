from models.Neo4j.clients import get_clients_by_locker
from models.Neo4j.lockers import (
    get_all_lockers,
    get_locker,
    get_lockers_with_available_capacity,
)
from models.Neo4j.ports import get_port_by_locker


def resolve_lockers(obj, info):
    return get_all_lockers()


def resolve_locker(obj, info, locker_id):
    locker = get_locker(locker_id)
    return locker


def resolve_lockers_with_available_capacity(obj, info, minCapacity=1):
    return get_lockers_with_available_capacity(minCapacity)


def resolve_locker_port(obj, info):
    locker_id = obj.get("id")
    if locker_id:
        return get_port_by_locker(locker_id)
    return None


def resolve_locker_clients(obj, info):
    locker_id = obj.get("id")
    if locker_id:
        return get_clients_by_locker(locker_id)
    return []
