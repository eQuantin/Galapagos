from models.Neo4j.clients import (
    get_all_clients,
    get_client_by_name,
)
from models.Neo4j.lockers import get_locker_for_client


def resolve_clients(obj, info):
    return get_all_clients()


def resolve_client(obj, info, name):
    return get_client_by_name(name)


def resolve_client_locker(obj, info):
    client = obj.get("name")
    if client:
        return get_locker_for_client(client)
    return None
