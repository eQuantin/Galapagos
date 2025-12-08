from models.Neo4j.seaplanes import get_seaplane, update_seaplane_status


class MaintenanceError(Exception):
    pass


def move_seaplane_into_maintenance(seaplane_name):
    # Verify seaplane exists
    seaplane = get_seaplane(seaplane_name)
    if not seaplane:
        raise MaintenanceError(f"Seaplane '{seaplane_name}' not found")

    # Update status to maintenance
    try:
        updated_seaplane = update_seaplane_status(seaplane_name, "maintenance")
        if not updated_seaplane:
            raise MaintenanceError(
                f"Failed to update seaplane '{seaplane_name}' status"
            )

        return {
            "success": True,
            "message": f"Seaplane '{seaplane_name}' has been moved into maintenance",
            "seaplane": updated_seaplane,
            "previous_status": "unknown",
            "new_status": "maintenance",
        }
    except Exception as e:
        raise MaintenanceError(f"Error moving seaplane into maintenance: {str(e)}")


def move_seaplane_out_of_maintenance(seaplane_name):
    seaplane = get_seaplane(seaplane_name)
    if not seaplane:
        raise MaintenanceError(f"Seaplane '{seaplane_name}' not found")

    try:
        updated_seaplane = update_seaplane_status(seaplane_name, "docked")
        if not updated_seaplane:
            raise MaintenanceError(
                f"Failed to update seaplane '{seaplane_name}' status"
            )

        return {
            "success": True,
            "message": f"Seaplane '{seaplane_name}' has been moved out of maintenance and is now docked",
            "seaplane": updated_seaplane,
            "previous_status": "maintenance",
            "new_status": "docked",
        }
    except Exception as e:
        raise MaintenanceError(f"Error moving seaplane out of maintenance: {str(e)}")


def get_seaplanes_in_maintenance():
    from models.Neo4j.seaplanes import get_seaplanes_by_status

    try:
        seaplanes = get_seaplanes_by_status("maintenance")
        return seaplanes
    except Exception as e:
        raise MaintenanceError(f"Error retrieving seaplanes in maintenance: {str(e)}")
