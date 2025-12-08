from models.Mongo.orders import (
    cancel_order,
    create_order,
    get_all_orders,
    get_order_by_id,
    get_orders_by_client,
    get_orders_by_status,
    get_orders_by_warehouse,
    update_order_status,
)
from models.Neo4j.clients import get_client_by_id
from models.Neo4j.lockers import get_locker, get_locker_for_client
from models.Neo4j.warehouse import get_warehouse_by_id


def resolve_orders(obj, info):
    return get_all_orders()


def resolve_order(obj, info, id):
    return get_order_by_id(id)


def resolve_orders_by_client(obj, info, client_id):
    return get_orders_by_client(client_id)


def resolve_orders_by_warehouse(obj, info, warehouse_id):
    return get_orders_by_warehouse(warehouse_id)


def resolve_orders_by_status(obj, info, status):
    return get_orders_by_status(status)


def resolve_create_order(obj, info, client_id, warehouse_id, crateQuantity):
    # Validate client exists
    client = get_client_by_id(client_id)
    if not client:
        return {
            "success": False,
            "message": f"Client '{client_id}' not found",
            "order": None,
        }

    # Validate warehouse exists
    warehouse = get_warehouse_by_id(warehouse_id)
    if not warehouse:
        return {
            "success": False,
            "message": f"Warehouse '{warehouse_id}' not found",
            "order": None,
        }

    # Get client's locker
    locker = get_locker_for_client(client["name"])
    if not locker:
        return {
            "success": False,
            "message": f"Client '{client['name']}' does not have an assigned locker",
            "order": None,
        }

    # Check locker capacity
    if locker.get("remaining_capacity", 0) < crateQuantity:
        return {
            "success": False,
            "message": f"Insufficient locker capacity. Available: {locker.get('remaining_capacity', 0)}, Required: {crateQuantity}",
            "order": None,
        }

    # Create the order
    try:
        order = create_order(
            client_id=client_id,
            warehouse_id=warehouse_id,
            locker_id=locker["id"],
            crate_quantity=crateQuantity,
        )

        return {
            "success": True,
            "message": f"Order created successfully with ID: {order['id']}",
            "order": order,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create order: {str(e)}",
            "order": None,
        }


def resolve_update_order_status(obj, info, orderId, status):
    """Resolver to update order status"""
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

    if status not in valid_statuses:
        return {
            "success": False,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            "order": None,
        }

    order = update_order_status(orderId, status)

    if order:
        return {
            "success": True,
            "message": f"Order status updated to '{status}'",
            "order": order,
        }
    else:
        return {
            "success": False,
            "message": f"Failed to update order status. Order ID '{orderId}' may not exist",
            "order": None,
        }


def resolve_cancel_order(obj, info, orderId, reason=None):
    """Resolver to cancel an order"""
    order = cancel_order(orderId, reason)

    if order:
        return {
            "success": True,
            "message": "Order cancelled successfully",
            "order": order,
        }
    else:
        return {
            "success": False,
            "message": f"Failed to cancel order. Order ID '{orderId}' may not exist",
            "order": None,
        }


# Nested field resolvers for Order type
def resolve_order_client(order, info):
    client = order.get("client_id")
    if client:
        return get_client_by_id(client)
    return None


def resolve_order_warehouse(order, info):
    warehouse = order.get("warehouse_id")
    if warehouse:
        return get_warehouse_by_id(warehouse)
    return None


def resolve_order_locker(order, info):
    locker = order.get("locker_id")
    if locker:
        return get_locker(locker)
    return None
