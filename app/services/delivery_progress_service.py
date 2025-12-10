from datetime import datetime, timedelta

from models.Mongo.deliveries import get_delivery_by_id, update_delivery_status
from models.Mongo.orders import update_order_status
from models.Neo4j.ports import get_distance_between_ports, get_port
from models.Neo4j.seaplanes import (
    get_seaplane,
    update_seaplane_location,
    update_seaplane_status,
)
from models.Neo4j.seaplanes_models import get_model_by_seaplane


def calculate_delivery_progress(delivery_id):
    """
    Automatically calculate the current state of a delivery based on elapsed time.

    This determines:
    - Which leg of the journey the plane is on
    - Whether it's flying or stopped at a port
    - Current position if flying
    - Whether delivery is complete

    Args:
        delivery_id: ID of the delivery

    Returns:
        Dictionary with:
            - status: Current status (pending, flying, stopped, completed)
            - current_leg: Index of current route segment
            - current_port: Port name if stopped, None if flying
            - next_port: Next destination port
            - position: {lat, lon} if flying, None if stopped
            - progress_percent: Progress on current leg
            - time_at_port: Minutes spent at current port (if stopped)
            - can_depart: Whether the 1-hour wait is complete
    """
    delivery = get_delivery_by_id(delivery_id)
    if not delivery:
        return None

    status = delivery.get("status")

    # If pending or completed, return basic info
    if status == "pending":
        return {
            "status": "pending",
            "current_leg": 0,
            "current_port": delivery["route"][0],
            "next_port": delivery["route"][1] if len(delivery["route"]) > 1 else None,
            "position": None,
            "progress_percent": 0,
            "time_at_port": None,
            "can_depart": False,
        }

    if status == "completed":
        route = delivery["route"]
        return {
            "status": "completed",
            "current_leg": len(route) - 1,
            "current_port": route[-1],
            "next_port": None,
            "position": None,
            "progress_percent": 100,
            "time_at_port": None,
            "can_depart": False,
        }

    if status != "in_progress":
        return None

    # Get delivery metadata
    route = delivery["route"]
    seaplane_name = delivery["seaplane_name"]
    started_at = delivery.get("started_at")

    if not started_at or not isinstance(started_at, datetime):
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.rstrip("Z"))
        else:
            return None

    # Get seaplane speed
    seaplane_model = get_model_by_seaplane(seaplane_name)
    if not seaplane_model:
        return None

    speed_kmh = seaplane_model.get("average_speed_kmh", 0)
    if speed_kmh <= 0:
        return None

    # Calculate total elapsed time since start
    current_time = datetime.utcnow()
    total_elapsed_hours = (current_time - started_at).total_seconds() / 3600

    # Simulate the journey from start
    time_accumulated = 0.0
    current_leg = 0

    for i in range(len(route) - 1):
        from_port = route[i]
        to_port = route[i + 1]

        # Get distance for this leg
        distance_km = get_distance_between_ports(from_port, to_port)
        if distance_km is None:
            return None

        # Calculate travel time for this leg
        travel_time_hours = distance_km / speed_kmh

        # Check if we're currently on this leg (flying)
        if time_accumulated + travel_time_hours > total_elapsed_hours:
            # We're flying on this leg
            time_into_leg = total_elapsed_hours - time_accumulated
            progress = time_into_leg / travel_time_hours

            # Calculate position
            from_port_obj = get_port(from_port)
            to_port_obj = get_port(to_port)

            if from_port_obj and to_port_obj:
                from services.flight_tracking_service import interpolate_great_circle

                lat, lon = interpolate_great_circle(
                    from_port_obj["latitude"],
                    from_port_obj["longitude"],
                    to_port_obj["latitude"],
                    to_port_obj["longitude"],
                    progress,
                )
                position = {"latitude": round(lat, 6), "longitude": round(lon, 6)}
            else:
                position = None

            return {
                "status": "flying",
                "current_leg": i,
                "current_port": None,
                "next_port": to_port,
                "departure_port": from_port,
                "position": position,
                "progress_percent": round(progress * 100, 2),
                "time_at_port": None,
                "can_depart": False,
            }

        # Add travel time
        time_accumulated += travel_time_hours

        # Check if we're stopped at this port (not the final destination)
        if i < len(route) - 2:  # Not the last port
            # 1 hour stop at each intermediate port
            if time_accumulated + 1.0 > total_elapsed_hours:
                # We're stopped at this port
                time_at_port_hours = total_elapsed_hours - time_accumulated
                time_at_port_minutes = time_at_port_hours * 60
                can_depart = time_at_port_hours >= 1.0

                return {
                    "status": "stopped",
                    "current_leg": i,
                    "current_port": to_port,
                    "next_port": route[i + 2] if i + 2 < len(route) else None,
                    "position": None,
                    "progress_percent": 0,
                    "time_at_port": round(time_at_port_minutes, 1),
                    "can_depart": can_depart,
                }

            # Add stop time
            time_accumulated += 1.0

        current_leg = i + 1

    # We've reached the final destination - mark as completed
    if status == "in_progress":
        # Auto-complete the delivery
        update_delivery_status(delivery_id, "completed")

        # Update all orders to delivered
        for order_id in delivery.get("order_ids", []):
            update_order_status(order_id, "delivered")

        # Update seaplane status to docked at warehouse
        update_seaplane_status(seaplane_name, "docked")
        update_seaplane_location(seaplane_name, route[-1])

    return {
        "status": "completed",
        "current_leg": len(route) - 1,
        "current_port": route[-1],
        "next_port": None,
        "position": None,
        "progress_percent": 100,
        "time_at_port": None,
        "can_depart": False,
    }


def get_delivery_status_with_progress(delivery_id):
    """
    Get complete delivery status including automatic progress calculation.

    Args:
        delivery_id: ID of the delivery

    Returns:
        Dictionary with delivery info and calculated progress
    """
    delivery = get_delivery_by_id(delivery_id)
    if not delivery:
        return {"success": False, "message": "Delivery not found"}

    progress = calculate_delivery_progress(delivery_id)

    return {
        "success": True,
        "delivery": delivery,
        "progress": progress,
    }


def update_seaplane_state_for_delivery(delivery_id):
    """
    Update seaplane Neo4j state based on current delivery progress.
    This ensures the seaplane location and status match the calculated position.

    Args:
        delivery_id: ID of the delivery
    """
    progress = calculate_delivery_progress(delivery_id)
    if not progress:
        return

    delivery = get_delivery_by_id(delivery_id)
    if not delivery:
        return

    seaplane_name = delivery.get("seaplane_name")
    if not seaplane_name:
        return

    status = progress.get("status")

    if status == "flying":
        # Update to flying status (removes DOCKED_AT)
        update_seaplane_status(seaplane_name, "flying")

        # Set flight tracking info for position calculation
        from models.Neo4j.seaplanes import start_seaplane_flight

        departure_port = progress.get("departure_port")
        next_port = progress.get("next_port")

        if departure_port and next_port:
            # Calculate when this leg started
            delivery_started = delivery.get("started_at")
            if isinstance(delivery_started, str):
                delivery_started = datetime.fromisoformat(delivery_started.rstrip("Z"))

            # This would need to calculate the exact departure time for this leg
            # For simplicity, we use the route segment info
            start_seaplane_flight(
                seaplane_name, departure_port, next_port, delivery_started
            )

    elif status == "stopped":
        # Update to docked at current port
        current_port = progress.get("current_port")
        if current_port:
            update_seaplane_status(seaplane_name, "docked")
            update_seaplane_location(seaplane_name, current_port)

    elif status == "completed":
        # Ensure seaplane is docked at final port
        current_port = progress.get("current_port")
        if current_port:
            update_seaplane_status(seaplane_name, "docked")
            update_seaplane_location(seaplane_name, current_port)
