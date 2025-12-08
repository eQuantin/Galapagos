from models.Neo4j.seaplanes import get_seaplanes_by_status
from models.Neo4j.seaplanes_status import get_all_status, get_status


def resolve_statuses(obj, info):
    return get_all_status()


def resolve_status(obj, info, value):
    return get_status(value)


def resolve_status_seaplane(obj, info):
    status = obj.get("value")
    if status:
        return get_seaplanes_by_status(status)
    return None
