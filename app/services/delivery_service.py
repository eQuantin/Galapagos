from datetime import datetime

from models.Mongo.deliveries import (
    create_delivery,
    get_delivery_by_id,
    update_delivery_status,
)
from models.Mongo.orders import get_order_by_id, update_order_status
from models.Neo4j.lockers import get_locker
from models.Neo4j.ports import (
    get_port_by_locker,
    get_port_by_seaplane,
    get_port_by_warehouse,
)
from models.Neo4j.seaplanes import (
    get_seaplane,
    start_seaplane_flight,
    update_seaplane_status,
)
from models.Neo4j.seaplanes_models import get_model_by_seaplane
from models.Neo4j.warehouse import get_warehouse_by_id
from services.routing_service import find_optimal_route


def create_delivery_from_orders(order_ids, seaplane_name):
    """
    Create a delivery from multiple orders.
    Validates orders, calculates optimal route, creates delivery record.

    Args:
        order_ids: List of order IDs to include in delivery
        seaplane_name: Name of the seaplane to use

    Returns:
        Dictionary with success status, message, and delivery data
    """
    if not order_ids or len(order_ids) == 0:
        return {
            "success": False,
            "message": "No orders provided",
            "delivery": None,
        }

    # Fetch and validate all orders
    orders = []
    warehouse_id = None
    warehouse_port = None
    delivery_ports = []

    for order_id in order_ids:
        order = get_order_by_id(order_id)

        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} not found",
                "delivery": None,
            }

        # Check order status
        if order["status"] != "pending":
            return {
                "success": False,
                "message": f"Order {order_id} is not pending (status: {order['status']})",
                "delivery": None,
            }

        # Validate all orders are from same warehouse
        if warehouse_id is None:
            warehouse_id = order["warehouse_id"]
            warehouse = get_warehouse_by_id(warehouse_id)
            if not warehouse:
                return {
                    "success": False,
                    "message": f"Warehouse {warehouse_id} not found",
                    "delivery": None,
                }
            warehouse_port_data = get_port_by_warehouse(warehouse["name"])
            if not warehouse_port_data:
                return {
                    "success": False,
                    "message": f"Warehouse {warehouse['name']} has no port",
                    "delivery": None,
                }
            warehouse_port = warehouse_port_data["name"]
        elif order["warehouse_id"] != warehouse_id:
            return {
                "success": False,
                "message": "All orders must be from the same warehouse",
                "delivery": None,
            }

        # Get delivery port (locker port)
        locker = get_locker(order["locker_id"])
        if not locker:
            return {
                "success": False,
                "message": f"Locker {order['locker_id']} not found",
                "delivery": None,
            }

        locker_port = get_port_by_locker(order["locker_id"])
        if not locker_port:
            return {
                "success": False,
                "message": f"Locker {order['locker_id']} has no port",
                "delivery": None,
            }

        delivery_ports.append(locker_port)
        orders.append(order)

    # Validate seaplane
    seaplane = get_seaplane(seaplane_name)
    if not seaplane:
        return {
            "success": False,
            "message": f"Seaplane {seaplane_name} not found",
            "delivery": None,
        }

    # Check if seaplane is at warehouse port
    seaplane_port = get_port_by_seaplane(seaplane_name)
    if not seaplane_port or seaplane_port["name"] != warehouse_port:
        return {
            "success": False,
            "message": f"Seaplane {seaplane_name} is not at warehouse port {warehouse_port}",
            "delivery": None,
        }

    # Calculate optimal route
    route_info = find_optimal_route(warehouse_port, delivery_ports)

    if not route_info or not route_info.get("route"):
        return {
            "success": False,
            "message": "Could not calculate valid route",
            "delivery": None,
        }

    # Get seaplane model for duration calculation
    seaplane_model = get_model_by_seaplane(seaplane_name)
    if not seaplane_model:
        return {
            "success": False,
            "message": f"Could not find model for seaplane {seaplane_name}",
            "delivery": None,
        }

    # Calculate estimated duration
    # num_delivery_stops = len(set(delivery_ports))
    # estimated_duration = calculate_estimated_duration(
    #     route_info["total_distance_km"],
    #     seaplane_model["average_speed_kmh"],
    #     num_delivery_stops,
    # )

    # Create delivery
    delivery = create_delivery(
        order_ids=order_ids,
        seaplane_name=seaplane_name,
        route=route_info["route"],
        total_distance_km=route_info["total_distance_km"],
        estimated_duration_hours=estimated_duration,
    )

    # Update orders to "processing" status
    for order_id in order_ids:
        update_order_status(order_id, "processing")

    return {
        "success": True,
        "message": f"Delivery created successfully with {len(order_ids)} orders",
        "delivery": delivery,
    }


def start_delivery(delivery_id):
    """
    Start a delivery - begins the automatic journey.
    The system will automatically track progress based on elapsed time.

    Args:
        delivery_id: ID of the delivery to start

    Returns:
        Dictionary with success status and message
    """
    delivery = get_delivery_by_id(delivery_id)

    if not delivery:
        return {"success": False, "message": "Delivery not found"}

    if delivery["status"] != "pending":
        return {
            "success": False,
            "message": f"Delivery is not pending (status: {delivery['status']})",
        }

    # Update delivery status to in_progress
    updated_delivery = update_delivery_status(delivery_id, "in_progress")

    if not updated_delivery:
        return {"success": False, "message": "Failed to update delivery status"}

    # Get first leg of journey
    route = delivery["route"]
    if len(route) < 2:
        return {"success": False, "message": "Invalid route"}

    departure_port = route[0]
    destination_port = route[1]
    seaplane_name = delivery["seaplane_name"]

    # Set flight tracking information
    departure_time = datetime.utcnow()
    start_seaplane_flight(
        seaplane_name, departure_port, destination_port, departure_time
    )

    # Update seaplane status to flying
    update_seaplane_status(seaplane_name, "flying")

    return {
        "success": True,
        "message": "Delivery started. Progress will be calculated automatically based on time.",
        "delivery": updated_delivery,
    }
