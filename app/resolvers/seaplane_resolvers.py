from models.Neo4j.ports import get_port_by_seaplane
from models.Neo4j.seaplanes import (
    get_all_seaplanes,
    get_available_seaplanes,
    get_seaplane,
    update_seaplane_location,
)
from models.Neo4j.seaplanes_models import get_model_by_seaplane
from models.Neo4j.seaplanes_status import get_status_by_seaplane


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


def resolve_change_seaplane_location(obj, info, seaplaneName, newPortName):
    try:
        # Get previous port before updating
        previous_port = get_port_by_seaplane(seaplaneName)

        # Update the seaplane location
        updated_seaplane = update_seaplane_location(seaplaneName, newPortName)

        if not updated_seaplane:
            return {
                "success": False,
                "message": f"Failed to update seaplane '{seaplaneName}' location. Seaplane or port may not exist.",
                "seaplane": None,
                "previousPort": None,
                "newPort": None,
            }

        # Get the new port
        new_port = get_port_by_seaplane(seaplaneName)

        previous_port_name = previous_port.get("name") if previous_port else "unknown"

        return {
            "success": True,
            "message": f"Seaplane '{seaplaneName}' has been relocated from '{previous_port_name}' to '{newPortName}'",
            "seaplane": updated_seaplane,
            "previousPort": previous_port,
            "newPort": new_port,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error changing seaplane location: {str(e)}",
            "seaplane": None,
            "previousPort": None,
            "newPort": None,
        }
