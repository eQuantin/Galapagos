from models.Mongo.mongo_models import get_mongo_db

def insert_scientific_equipment(equipment_list):
    db = get_mongo_db()

    if not equipment_list:
        return

    db.equipment.insert_many(equipment_list)


def get_all_equipment():
    db = get_mongo_db()

    equipments = list(db.equipment.find())

    return equipments
