from models.Mongo.deliveries import (
    get_active_delivery_for_seaplane,
    get_all_deliveries,
    get_deliveries_by_seaplane,
    get_deliveries_by_status,
    get_delivery_by_id,
)
from models.Mongo.orders import get_order_by_id
from models.Neo4j.seaplanes import get_seaplane
from services.delivery_progress_service import (
    calculate_delivery_progress,
)
from services.delivery_service import create_delivery_from_orders, start_delivery

# ============================================================================
# Query Resolvers
# ============================================================================


def resolve_deliveries(obj, info):
    """Get all deliveries."""
    return get_all_deliveries()


def resolve_delivery(obj, info, id):
    """Get a single delivery by ID."""
    return get_delivery_by_id(id)


def resolve_deliveries_by_seaplane(obj, info, seaplaneName):
    """Get all deliveries for a specific seaplane."""
    return get_deliveries_by_seaplane(seaplaneName)


def resolve_deliveries_by_status(obj, info, status):
    """Get all deliveries with a specific status."""
    return get_deliveries_by_status(status)


def resolve_active_delivery_for_seaplane(obj, info, seaplaneName):
    """Get the active (in_progress) delivery for a seaplane."""
    return get_active_delivery_for_seaplane(seaplaneName)


def resolve_delivery_progress(obj, info, deliveryId):
    """
    Get automatic progress calculation for a delivery.
    Returns current position, leg, and status based on elapsed time.
    """
    return calculate_delivery_progress(deliveryId)


# ============================================================================
# Mutation Resolvers
# ============================================================================


def resolve_create_delivery(obj, info, orderIds, seaplaneName):
    """
    Create a new delivery from multiple orders.
    Calculates optimal route automatically.
    """
    result = create_delivery_from_orders(orderIds, seaplaneName)
    return result


def resolve_start_delivery(obj, info, deliveryId):
    """
    Start a delivery - begins automatic journey.
    Progress is calculated automatically based on elapsed time.
    """
    result = start_delivery(deliveryId)

    # If successful, fetch the delivery
    if result.get("success"):
        delivery = get_delivery_by_id(deliveryId)
        result["delivery"] = delivery

    return result


# ============================================================================
# Nested Field Resolvers
# ============================================================================


def resolve_delivery_seaplane(obj, info):
    """Resolve the seaplane for a delivery."""
    seaplane_name = obj.get("seaplane_name")
    if seaplane_name:
        return get_seaplane(seaplane_name)
    return None


def resolve_delivery_orders(obj, info):
    """Resolve the orders for a delivery."""
    order_ids = obj.get("order_ids", [])
    orders = []

    for order_id in order_ids:
        order = get_order_by_id(order_id)
        if order:
            orders.append(order)

    return orders


def resolve_delivery_progress_field(obj, info):
    """
    Resolve the automatic progress for a delivery.
    Calculates current state based on elapsed time.
    """
    delivery_id = obj.get("id") or obj.get("_id")
    if delivery_id:
        return calculate_delivery_progress(str(delivery_id))
    return None
