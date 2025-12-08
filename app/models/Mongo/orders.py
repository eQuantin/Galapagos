from datetime import datetime

from bson import ObjectId
from models.Mongo.mongo_models import get_mongo_db


def create_order(client_id, warehouse_id, locker_id, crate_quantity):
    db = get_mongo_db()

    order = {
        "client_id": client_id,
        "warehouse_id": warehouse_id,
        "locker_id": locker_id,
        "crate_quantity": crate_quantity,
        "status": "pending",  # pending, processing, shipped, delivered, cancelled
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "delivered_at": None,
    }

    result = db.orders.insert_one(order)
    order["_id"] = str(result.inserted_id)
    order["id"] = order["_id"]

    return order


def get_all_orders():
    db = get_mongo_db()
    orders = list(db.orders.find().sort("created_at", -1))

    # Convert ObjectId to string
    for order in orders:
        order["_id"] = str(order["_id"])
        order["id"] = order["_id"]

    return orders


def get_order_by_id(order_id):
    db = get_mongo_db()

    try:
        order = db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
            order["id"] = order["_id"]
        return order
    except Exception:
        return None


def get_orders_by_client(client_id):
    db = get_mongo_db()
    orders = list(db.orders.find({"client_id": client_id}).sort("created_at", -1))

    for order in orders:
        order["_id"] = str(order["_id"])
        order["id"] = order["_id"]

    return orders


def get_orders_by_warehouse(warehouse_id):
    db = get_mongo_db()
    orders = list(db.orders.find({"warehouse_id": warehouse_id}).sort("created_at", -1))

    for order in orders:
        order["_id"] = str(order["_id"])
        order["id"] = order["_id"]

    return orders


def get_orders_by_status(status):
    db = get_mongo_db()
    orders = list(db.orders.find({"status": status}).sort("created_at", -1))

    for order in orders:
        order["_id"] = str(order["_id"])
        order["id"] = order["_id"]

    return orders


def update_order_status(order_id, new_status):
    db = get_mongo_db()

    try:
        update_data = {"status": new_status, "updated_at": datetime.utcnow()}

        # If status is delivered, set delivered_at timestamp
        if new_status == "delivered":
            update_data["delivered_at"] = datetime.utcnow()

        result = db.orders.update_one(
            {"_id": ObjectId(order_id)}, {"$set": update_data}
        )

        if result.modified_count > 0:
            return get_order_by_id(order_id)
        return None
    except Exception:
        return None


def update_order(order_id, update_fields):
    db = get_mongo_db()

    try:
        update_fields["updated_at"] = datetime.utcnow()

        result = db.orders.update_one(
            {"_id": ObjectId(order_id)}, {"$set": update_fields}
        )

        if result.modified_count > 0:
            return get_order_by_id(order_id)
        return None
    except Exception:
        return None


def cancel_order(order_id, reason=None):
    db = get_mongo_db()

    try:
        update_data = {"status": "cancelled", "updated_at": datetime.utcnow()}

        if reason:
            update_data["cancellation_reason"] = reason

        result = db.orders.update_one(
            {"_id": ObjectId(order_id)}, {"$set": update_data}
        )

        if result.modified_count > 0:
            return get_order_by_id(order_id)
        return None
    except Exception:
        return None


def delete_order(order_id):
    db = get_mongo_db()

    try:
        result = db.orders.delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count > 0
    except Exception:
        return False


def get_order_statistics():
    db = get_mongo_db()

    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_crates": {"$sum": "$crate_quantity"},
            }
        }
    ]

    stats = list(db.orders.aggregate(pipeline))

    return {"by_status": stats, "total_orders": db.orders.count_documents({})}
