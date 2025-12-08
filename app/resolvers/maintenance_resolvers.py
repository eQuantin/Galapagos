from services.seaplane_maintenance_service import (
    MaintenanceError,
    get_seaplanes_in_maintenance,
    move_seaplane_into_maintenance,
    move_seaplane_out_of_maintenance,
)


def resolve_move_seaplane_into_maintenance(obj, info, seaplaneName):
    try:
        result = move_seaplane_into_maintenance(seaplaneName)
        return {
            "success": result["success"],
            "message": result["message"],
            "seaplane": result["seaplane"],
        }
    except MaintenanceError as e:
        return {
            "success": False,
            "message": str(e),
            "seaplane": None,
        }


def resolve_move_seaplane_out_of_maintenance(obj, info, seaplaneName):
    try:
        result = move_seaplane_out_of_maintenance(seaplaneName)
        return {
            "success": result["success"],
            "message": result["message"],
            "seaplane": result["seaplane"],
        }
    except MaintenanceError as e:
        return {
            "success": False,
            "message": str(e),
            "seaplane": None,
        }


def resolve_seaplanes_in_maintenance(obj, info):
    try:
        return get_seaplanes_in_maintenance()
    except MaintenanceError as e:
        print(f"Error retrieving seaplanes in maintenance: {e}")
        return []
