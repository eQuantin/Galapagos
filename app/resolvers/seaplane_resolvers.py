from models.Neo4j.ports import get_port_by_seaplane
from models.Neo4j.seaplanes import (
    get_all_seaplanes,
    get_available_seaplanes,
    get_seaplane,
)
from models.Neo4j.seaplanes_models import get_model_by_seaplane
from models.Neo4j.seaplanes_status import get_status_by_seaplane
from services.flight_tracking_service import calculate_current_position


def resolve_seaplanes(obj, info):
    return get_all_seaplanes()


def resolve_seaplane(obj, info, name):
    return get_seaplane(name)


def resolve_seaplane_model(obj, info):
    seaplane = obj.get("name")
    if seaplane:
        return get_model_by_seaplane(seaplane)
    return None


def resolve_seaplane_port(obj, info):
    seaplane = obj.get("name")
    if seaplane:
        return get_port_by_seaplane(seaplane)
    return None


def resolve_seaplane_status(obj, info):
    seaplane = obj.get("name")
    if seaplane:
        return get_status_by_seaplane(seaplane)
    return None


def resolve_available_seaplanes(obj, info, portName=None):
    return get_available_seaplanes(portName)


def resolve_seaplane_current_position(obj, info):
    seaplane_name = obj.get("name")
    if seaplane_name:
        return calculate_current_position(seaplane_name)
    return None
