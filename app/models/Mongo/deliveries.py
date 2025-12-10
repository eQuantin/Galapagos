from datetime import datetime

from bson import ObjectId
from models.Mongo.mongo_models import get_mongo_db


def create_delivery(order_ids, seaplane_name, route, total_distance_km):
    db = get_mongo_db()

    delivery = {
        "order_ids": order_ids,
        "seaplane_name": seaplane_name,
        "route": route,
        "current_port_index": 0,
        "total_distance_km": total_distance_km,
        "status": "pending",  # pending, in_progress, completed, cancelled
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "current_stop_arrival_time": None,
    }

    result = db.deliveries.insert_one(delivery)
    delivery["_id"] = str(result.inserted_id)
    delivery["id"] = delivery["_id"]

    return delivery


def get_all_deliveries():
    db = get_mongo_db()
    deliveries = list(db.deliveries.find().sort("created_at", -1))

    for delivery in deliveries:
        delivery["_id"] = str(delivery["_id"])
        delivery["id"] = delivery["_id"]

    return deliveries


def get_delivery_by_id(delivery_id):
    db = get_mongo_db()

    try:
        delivery = db.deliveries.find_one({"_id": ObjectId(delivery_id)})
        if delivery:
            delivery["_id"] = str(delivery["_id"])
            delivery["id"] = delivery["_id"]
        return delivery
    except Exception:
        return None


def get_deliveries_by_seaplane(seaplane_name):
    db = get_mongo_db()
    deliveries = list(
        db.deliveries.find({"seaplane_name": seaplane_name}).sort("created_at", -1)
    )

    for delivery in deliveries:
        delivery["_id"] = str(delivery["_id"])
        delivery["id"] = delivery["_id"]

    return deliveries


def get_deliveries_by_status(status):
    db = get_mongo_db()
    deliveries = list(db.deliveries.find({"status": status}).sort("created_at", -1))

    for delivery in deliveries:
        delivery["_id"] = str(delivery["_id"])
        delivery["id"] = delivery["_id"]

    return deliveries


def get_active_delivery_for_seaplane(seaplane_name):
    db = get_mongo_db()
    delivery = db.deliveries.find_one(
        {"seaplane_name": seaplane_name, "status": "in_progress"}
    )

    if delivery:
        delivery["_id"] = str(delivery["_id"])
        delivery["id"] = delivery["_id"]

    return delivery


def update_delivery_status(delivery_id, new_status):
    db = get_mongo_db()

    try:
        update_data = {"status": new_status}

        if new_status == "in_progress":
            update_data["started_at"] = datetime.utcnow()
        elif new_status == "completed":
            update_data["completed_at"] = datetime.utcnow()

        result = db.deliveries.update_one(
            {"_id": ObjectId(delivery_id)}, {"$set": update_data}
        )

        if result.modified_count > 0:
            return get_delivery_by_id(delivery_id)
        return None
    except Exception:
        return None


def update_delivery_progress(
    delivery_id, current_port_index, current_stop_arrival_time=None
):
    db = get_mongo_db()

    try:
        update_data = {
            "current_port_index": current_port_index,
        }

        if current_stop_arrival_time:
            update_data["current_stop_arrival_time"] = current_stop_arrival_time

        result = db.deliveries.update_one(
            {"_id": ObjectId(delivery_id)}, {"$set": update_data}
        )

        if result.modified_count > 0:
            return get_delivery_by_id(delivery_id)
        return None
    except Exception:
        return None
